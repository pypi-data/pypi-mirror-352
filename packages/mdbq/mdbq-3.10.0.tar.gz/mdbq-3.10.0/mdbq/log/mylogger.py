import logging
import logging.handlers
import datetime
import json
import os
import sys
import time
import threading
import queue
from typing import Optional, Dict, Any, List, Callable, Union
import atexit
import traceback
import inspect

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class MyLogger:
    """
    日志记录器

    功能：
    - 异步日志记录（减少I/O阻塞）
    - 上下文管理器支持
    - 自定义日志过滤器
    - 更丰富的系统指标采集
    - 日志采样控制
    - 动态日志级别调整
    - 请求跟踪ID
    - 多线程安全
    - 日志缓冲和批量写入
    - 自定义异常处理

    使用示例：
    logger = MyLogger(
        name='app_logger',
        logging_mode='both',
        log_level='INFO',
        log_file='app.log',
        max_log_size=50,
        backup_count=5,
        enable_async=True
    )

    with logger.context(request_id='12345'):
        logger.info("处理请求", extra={'user': 'admin'})
    """

    def __init__(
            self,
            name: str = 'mylogger.log',
            logging_mode: str = 'console',  # 'both', 'console', 'file', 'none'
            log_level: str = 'INFO',  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
            log_file: str = 'm_app.log',
            log_format: str = 'json',  # 默认json格式，可选'simple'
            max_log_size: int = 50,  # MB
            backup_count: int = 5,
            sensitive_fields: Optional[List[str]] = None,
            enable_async: bool = False,
            buffer_size: int = 1000,
            sample_rate: float = 1.0,
            filters: Optional[List[Callable]] = None,
            enable_metrics: bool = False,
            metrics_interval: int = 300,
            message_limited: int = 1000,
            flush_interval: int = 5
    ):
        """
        初始化日志器

        :param name: 日志器名称
        :param logging_mode: 输出模式
        :param log_level: 日志级别
        :param log_file: 日志文件路径
        :param max_log_size: 单个日志文件最大大小(MB)
        :param backup_count: 保留的日志文件数量
        :param sensitive_fields: 敏感字段列表(会被过滤)
        :param enable_async: 是否启用异步日志
        :param buffer_size: 日志缓冲大小(仅异步模式有效)
        :param sample_rate: 控制日志的采样率(0.0-1.0)，使用消息内容的哈希值来决定是否记录，减少日志量，防止日志过于冗长
        :param filters: 自定义日志过滤器列表
        :param enable_metrics: 是否启用系统指标采集
        :param metrics_interval: 指标采集间隔(秒)
        :param message_limited: 简化日志内容，避免过长
        :param flush_interval: 定时刷新日志器间隔(秒)
        """
        log_path = os.path.join(os.path.expanduser("~"), 'logfile')
        self.name = name
        self.logging_mode = logging_mode.lower()
        self.log_level = log_level.upper()
        self.log_file = os.path.join(log_path, log_file)
        if not os.path.isdir(os.path.dirname(self.log_file)):
            os.makedirs(os.path.dirname(self.log_file))
        self.log_format = log_format
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        self.sensitive_fields = sensitive_fields or []
        self.enable_async = enable_async
        self.buffer_size = buffer_size
        self.sample_rate = max(0.0, min(1.0, sample_rate))
        self.filters = filters or []
        self.enable_metrics = enable_metrics and HAS_PSUTIL
        self.metrics_interval = metrics_interval
        self.message_limited = message_limited
        self.flush_interval = flush_interval

        # 上下文相关
        self._context = threading.local()
        self._context.data = {}

        # 系统指标相关
        self._last_metrics_time = 0
        self._metrics_cache = {}

        # 异步日志相关
        self._log_queue = queue.Queue(maxsize=buffer_size)
        self._async_thread = None
        self._stop_event = threading.Event()

        # 定时刷新相关
        self._flush_thread = None
        self._last_flush_time = 0
        self._start_flush_thread()

        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self._init_logging()

        if self.enable_async:
            self._start_async_logging()

        atexit.register(self.shutdown)

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.shutdown()
        if exc_type is not None:
            self.error(f"上下文内异常: {exc_val}",
                       extra={'类型': str(exc_type)})
        return False

    def context(self, **kwargs):
        """返回一个上下文管理器，可以设置临时上下文变量"""
        return self._ContextManager(self, kwargs)

    class _ContextManager:
        def __init__(self, logger, context_vars):
            self.logger = logger
            self.context_vars = context_vars
            self.old_context = {}

        def __enter__(self):
            # 保存旧上下文并设置新上下文
            self.old_context = getattr(self.logger._context, 'data', {}).copy()
            self.logger._context.data.update(self.context_vars)
            return self.logger

        def __exit__(self, exc_type, exc_val, exc_tb):
            # 恢复旧上下文
            self.logger._context.data = self.old_context
            if exc_type is not None:
                self.logger.error(f"上下文内异常2: {exc_val}",
                                  extra={'类型': str(exc_type)})
            return False

    def _init_logging(self):
        """初始化日志配置"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_levels:
            self.log_level = 'INFO'

        self.logger.setLevel(self.log_level)

        # 防止重复添加handler
        if self.logger.handlers:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

        # 定义日志格式
        if self.log_format.lower() == 'simple':
            # 简单文本格式
            class SimpleFormatter(logging.Formatter):
                def format(self, record):
                    # 基础日志信息
                    msg = super().format(record)

                    # 添加上下文信息
                    if hasattr(record, 'extra_data') and record.extra_data:
                        context_data = record.extra_data.get('context_data', {})
                        if context_data:
                            msg += f" | Context: {context_data}"

                        # 添加性能指标
                        metrics = record.extra_data.get('性能指标', {})
                        if metrics:
                            msg += f" | Metrics: {metrics}"

                        # 添加其他额外数据
                        extra = {k: v for k, v in record.extra_data.items()
                                 if k not in ('context_data', '性能指标')}
                        if extra:
                            msg += f" | Extra: {extra}"

                    return msg

            formatter = SimpleFormatter('%(asctime)s - %(levelname)s - %(message)s')
            formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        else:
            # 结构化JSON格式
            class StructuredFormatter(logging.Formatter):
                def format(self, record):
                    log_data = {
                        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'level': record.levelname,
                        'message': record.getMessage(),
                        # 'name': record.name,
                        # 'module': record.module,
                        # 'function': record.funcName,
                    }

                    # 添加额外字段
                    if hasattr(record, 'extra_data'):
                        log_data.update(record.extra_data)

                    # 添加上下文信息
                    if hasattr(record, 'context_data'):
                        log_data.update(record.context_data)

                    # 添加异常信息
                    if record.exc_info:
                        log_data['异常'] = self.formatException(record.exc_info)

                    # 过滤敏感信息
                    if hasattr(record, '过滤'):
                        for field in record.sensitive_fields:
                            if field in log_data:
                                log_data[field] = '***'
                            if isinstance(log_data.get('message'), str):
                                log_data['message'] = log_data['message'].replace(field, '***')

                    return json.dumps(log_data, ensure_ascii=False)

            formatter = StructuredFormatter()

        # 根据模式添加相应的handler
        if self.logging_mode in ('both', 'console'):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if self.logging_mode in ('both', 'file'):
            # 确保日志目录存在
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            file_handler = logging.handlers.RotatingFileHandler(
                filename=self.log_file,
                maxBytes=self.max_log_size * 1024 * 1024,
                backupCount=self.backup_count,
                encoding='utf-8',
                delay=False
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统资源使用指标"""
        if not self.enable_metrics:
            return {}

        try:
            return {
                '内存': {
                    '使用率': psutil.virtual_memory().percent,
                    '已使用': psutil.virtual_memory().used,
                    '可用': psutil.virtual_memory().available,
                },
                'CPU': {
                    '使用率': psutil.cpu_percent(),
                    '核心数': psutil.cpu_count(),
                },
                '磁盘': {
                    '使用率': psutil.disk_usage('/').percent,
                    '已使用': psutil.disk_usage('/').used,
                    '剩余': psutil.disk_usage('/').free,
                },
                '网络': {
                    '发送字节数': psutil.net_io_counters().bytes_sent,
                    '接收字节数': psutil.net_io_counters().bytes_recv,
                },
                '进程': {
                    'PID': os.getpid(),
                    '线程数': threading.active_count(),
                }
            }
        except Exception as e:
            self.logger.warning(f"无法采集系统性能指标: {e}",
                                extra={'extra_data': {'metrics_error': str(e)}})
            return {}

    def _apply_filters(self, level: str, message: str, extra: Dict) -> bool:
        """应用自定义过滤器"""
        for filter_func in self.filters:
            try:
                if not filter_func(level, message, extra):
                    return False  # 如果过滤器返回 False，则丢弃该日志
            except Exception as e:
                self.logger.warning(f"过滤失败: {e}",
                                    extra={'extra_data': {'filter_error': str(e)}})
        return True  # 所有过滤器都返回 True，则记录该日志

    def _async_log_worker(self):
        """异步日志工作线程"""
        while not self._stop_event.is_set() or not self._log_queue.empty():
            try:
                log_args = self._log_queue.get(timeout=0.1)
                if log_args:
                    level, message, extra = log_args
                    self._sync_log(level, message, extra)
            except queue.Empty:
                continue
            except Exception as e:
                # 防止日志线程崩溃
                try:
                    self.logger.error(f"日志线程崩溃: {e}",
                                      extra={'extra_data': {'async_error': str(e)}})
                except:
                    pass

    def _start_async_logging(self):
        """启动异步日志线程"""
        self._stop_event.clear()
        self._async_thread = threading.Thread(
            target=self._async_log_worker,
            name=f"{self.name}_async_logger",
            daemon=True
        )
        self._async_thread.start()

    def log_error_handler(retry_times=0, fallback_level='error'):
        """
        日志错误处理装饰器

        参数:
        - retry_times: 异常时重试次数
        - fallback_level: 降级日志级别
        """

        def decorator(log_method):
            def wrapper(self, level: str, message: str, extra: Optional[Dict] = None):
                last_exception = None
                for attempt in range(retry_times + 1):
                    try:
                        return log_method(self, level, message, extra)
                    except Exception as e:
                        last_exception = e
                        if attempt < retry_times:
                            time.sleep(0.1 * (attempt + 1))  # 简单的退避策略
                            continue

                        try:
                            # 降级处理
                            logging.basicConfig()
                            fallback_logger = logging.getLogger(f"{getattr(self, 'name', 'mylogger')}_fallback")
                            fallback_msg = f"[降级处理] {message}"[:1000]
                            getattr(fallback_logger, fallback_level)(
                                f"日志记录失败(尝试{attempt + 1}次): {e}\n原始消息: {fallback_msg}"
                            )
                        except:
                            sys.stderr.write(f"严重: 日志系统完全失败 - {last_exception}\n")

                return None

            return wrapper

        return decorator

    @log_error_handler(retry_times=1, fallback_level='warning')
    def _sync_log(self, level: str, message: str, extra: Optional[Dict] = None):
        """同步日志记录"""
        if not hasattr(self.logger, level.lower()):
            return

        # message 仅接收字符串类型
        if not isinstance(message, str):
            message = str(message)

        # 简化日志内容，避免过长
        if len(message) > self.message_limited:
            message = message[:self.message_limited] + '...'

        # 定期收集系统指标
        if self.enable_metrics:
            now = time.time()
            if now - self._last_metrics_time > self.metrics_interval:
                self._metrics_cache = self._get_system_metrics()
                self._last_metrics_time = now

        # 准备日志额外数据
        log_extra = {}
        if self.enable_metrics:
            log_extra['性能指标'] = self._metrics_cache
        if extra:
            log_extra.update(extra)

        # 添加上下文信息
        if hasattr(self._context, 'data') and self._context.data:
            log_extra['context_data'] = self._context.data.copy()

        # 添加敏感字段过滤
        if self.sensitive_fields:
            log_extra['过滤'] = self.sensitive_fields

        # 应用日志采样
        if self.sample_rate < 1.0 and level.lower() in ('debug', 'info'):
            if hash(message) % 100 >= self.sample_rate * 100:
                return

        # 应用过滤器
        if not self._apply_filters(level, message, log_extra):
            return

        # 记录日志
        getattr(self.logger, level.lower())(message, extra={'extra_data': log_extra})

    def log(self, level: str, message: str, extra: Optional[Dict] = None):
        """
        记录日志

        :param level: 日志级别 ('debug', 'info', 'warning', 'error', 'critical')
        :param message: 日志消息
        :param extra: 额外数据字典
        """
        if not hasattr(self.logger, level.lower()):
            return

        if self.enable_async:
            try:
                self._log_queue.put((level, message, extra), timeout=0.1)
            except queue.Full:
                # 队列满时降级为同步日志
                self._sync_log(level, f"[ASYNC QUEUE FULL] {message}", extra)
        else:
            self._sync_log(level, message, extra)

    def set_level(self, level: str):
        """动态设置日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        level = level.upper()
        if level in valid_levels:
            self.log_level = level
            self.logger.setLevel(level)
            for handler in self.logger.handlers:
                handler.setLevel(level)

    def add_filter(self, filter_func: Callable):
        """添加日志过滤器"""
        if callable(filter_func):
            self.filters.append(filter_func)

    def set_context(self, **kwargs):
        """设置上下文变量"""
        if not hasattr(self._context, 'data'):
            self._context.data = {}
        self._context.data.update(kwargs)

    def get_context(self, key: str, default=None):
        """获取上下文变量"""
        if hasattr(self._context, 'data'):
            return self._context.data.get(key, default)
        return default

    def clear_context(self):
        """清除所有上下文变量"""
        if hasattr(self._context, 'data'):
            self._context.data.clear()

    def debug(self, message: str, extra: Optional[Dict] = None):
        """记录调试信息"""
        self.log('debug', message, extra)

    def info(self, message: str, extra: Optional[Dict] = None):
        """记录一般信息"""
        self.log('info', message, extra)

    def warning(self, message: str, extra: Optional[Dict] = None):
        """记录警告信息"""
        self.log('warning', message, extra)

    def error(self, message: str, extra: Optional[Dict] = None):
        """记录错误信息"""
        self.log('error', message, extra)

    def critical(self, message: str, extra: Optional[Dict] = None):
        """记录严重错误信息"""
        self.log('critical', message, extra)

    def exception(self, message: str, exc_info: Exception, extra: Optional[Dict] = None):
        """记录异常信息"""
        if not extra:
            extra = {}

        # # 获取完整的异常堆栈
        # tb = exc_info.__traceback__
        # while tb.tb_next:
        #     tb = tb.tb_next  # 获取最内层的堆栈帧
        #
        # extra.update({
        #     'module': tb.tb_frame.f_globals.get('__name__', ''),
        #     'function': tb.tb_frame.f_code.co_name,
        #     'line': tb.tb_lineno,
        #     'file': tb.tb_frame.f_code.co_filename,
        #     '异常': str(exc_info),
        #     '类型': exc_info.__class__.__name__,
        #     '堆栈': self._format_traceback(exc_info)
        # })

        # 使用inspect获取调用栈
        frame = inspect.currentframe()
        try:
            # 向上追溯2层（1层是exception方法本身，2层是实际调用位置）
            caller_frame = frame.f_back.f_back
            extra.update({
                'module': caller_frame.f_globals.get('__name__', ''),
                'function': caller_frame.f_code.co_name,
                'line': caller_frame.f_lineno,
                'file': caller_frame.f_code.co_filename,
                '异常': str(exc_info),
                '类型': exc_info.__class__.__name__,
                '堆栈': self._format_traceback(exc_info)
            })
        finally:
            del frame  # 避免循环引用

        # 直接使用logger的error方法记录，保留原始调用栈
        self.log('error', message, extra)

    def _format_traceback(self, exc_info):
        """格式化异常堆栈"""
        if exc_info is None:
            return ""
        return ''.join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__))

    def timeit(self, message: str = "Execution time"):
        """返回一个计时器上下文管理器"""
        return self._Timer(self, message)

    class _Timer:
        def __init__(self, logger, message):
            self.logger = logger
            self.message = message
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed = time.time() - self.start_time
            self.logger.info(f"{self.message}: {elapsed:.3f}s",
                             extra={'elapsed_seconds': elapsed})
            return False

    def _start_flush_thread(self):
        """启动定时刷新线程"""
        self._stop_event.clear()
        self._flush_thread = threading.Thread(
            target=self._flush_worker,
            name=f"{self.name}_flush_thread",
            daemon=True
        )
        self._flush_thread.start()

    def _flush_worker(self):
        """定时刷新工作线程"""
        while not self._stop_event.is_set():
            try:
                time.sleep(self.flush_interval)
                self._flush_handlers()
            except Exception as e:
                try:
                    self.logger.error(f"刷新线程异常: {e}",
                                      extra={'extra_data': {'flush_error': str(e)}})
                except:
                    pass

    def _flush_handlers(self):
        """刷新所有handler"""
        for handler in self.logger.handlers:
            try:
                handler.flush()
            except Exception as e:
                try:
                    self.logger.error(f"刷新handler失败: {e}",
                                      extra={'extra_data': {'handler_flush_error': str(e)}})
                except:
                    pass

    def shutdown(self):
        """关闭日志记录器，确保所有日志被刷新"""
        if self.enable_async:
            self._stop_event.set()
            # 等待队列清空
            while not self._log_queue.empty():
                time.sleep(0.1)
            if self._async_thread and self._async_thread.is_alive():
                self._async_thread.join(timeout=0.5)

        # 确保所有handler被刷新
        if self._flush_thread:
            self._flush_handlers()
            if self._flush_thread.is_alive():
                self._flush_thread.join(timeout=0.5)

        # 关闭所有handler
        for handler in self.logger.handlers:
            try:
                handler.close()
            except:
                pass

def main():
    # 创建日志记录器
    logger = MyLogger(
        name='my_app',
        logging_mode='both',
        log_level='DEBUG',
        log_file='my_app.log',
        log_format='json',
        max_log_size=50,
        backup_count=5,
        enable_async=False,  # 是否启用异步日志
        sample_rate=1,  # 采样50%的DEBUG/INFO日志
        sensitive_fields=[],  #  敏感字段列表
        enable_metrics=False,  # 是否启用性能指标
    )

    logger.info('123')

    # 确保所有日志被刷新
    logger.shutdown()


if __name__ == '__main__':
    pass
