"""
基于structlog的函数装饰器，自动打印函数调用日志

使用方法：
    import structlog_wrap

    @structlog_wrap
    def my_function(arg1, arg2="default"):
        return arg1 + arg2
"""
import functools
import inspect
import sys
from datetime import datetime
from typing import Any, Callable, Dict, Tuple

import structlog


# 配置structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


class FunctionLogger:
    """函数日志记录器"""

    def __init__(self, function_name_width: int = 30):
        """
        初始化日志记录器

        Args:
            function_name_width: 函数名显示宽度，用于对齐（默认30以适应类名.方法名格式）
        """
        self.function_name_width = function_name_width
        self.logger = structlog.get_logger()

    def format_args(self, func: Callable, args: Tuple, kwargs: Dict[str, Any]) -> str:
        """
        格式化函数参数

        Args:
            func: 被调用的函数
            args: 位置参数
            kwargs: 关键字参数

        Returns:
            格式化后的参数字符串
        """
        # 获取函数签名
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # 格式化参数，过滤掉 self 和 cls
        arg_strs = []
        for name, value in bound_args.arguments.items():
            # 跳过 self 和 cls 参数
            if name in ('self', 'cls'):
                continue

            # 限制参数值的长度，避免日志过长
            if isinstance(value, str) and len(value) > 50:
                value_str = f'"{value[:47]}..."'
            elif isinstance(value, (list, dict, tuple)) and len(str(value)) > 50:
                value_str = f"{type(value).__name__}(len={len(value)})"
            else:
                value_str = repr(value)
            arg_strs.append(f"{name}={value_str}")

        return f"({', '.join(arg_strs)})"

    def log_function_call(self, func: Callable, args: Tuple, kwargs: Dict[str, Any]) -> None:
        """
        记录函数调用日志

        Args:
            func: 被调用的函数
            args: 位置参数
            kwargs: 关键字参数
        """
        # 获取当前时间
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取函数名，如果是类方法则包含类名
        func_name = self._get_full_function_name(func, args)

        # 格式化函数名（智能处理超长函数名）
        if len(func_name) > self.function_name_width:
            # 如果函数名超过设定宽度，截断并添加省略号
            if self.function_name_width > 3:
                func_name_padded = func_name[:self.function_name_width-3] + "..."
            else:
                # 如果宽度太小，直接截断
                func_name_padded = func_name[:self.function_name_width]
        else:
            # 如果函数名不超过宽度，正常左对齐
            func_name_padded = func_name.ljust(self.function_name_width)

        # 格式化参数
        args_str = self.format_args(func, args, kwargs)

        # 构造日志消息
        log_message = f"{timestamp} | {func_name_padded} | {args_str}"

        # 直接打印，不使用structlog的JSON格式
        print(log_message)

    def _get_full_function_name(self, func: Callable, args: Tuple) -> str:
        """
        获取完整的函数名，包括类名（如果适用）

        Args:
            func: 被调用的函数
            args: 位置参数

        Returns:
            完整的函数名，格式为 "类名.方法名" 或 "函数名"
        """
        func_name = func.__name__

        # 检查是否是类方法或实例方法
        if args:
            first_arg = args[0]

            # 检查是否是实例方法（第一个参数是实例）
            if hasattr(first_arg, '__class__') and hasattr(first_arg.__class__, func_name):
                class_name = first_arg.__class__.__name__
                return f"{class_name}.{func_name}"

            # 检查是否是类方法（第一个参数是类）
            elif isinstance(first_arg, type) and hasattr(first_arg, func_name):
                class_name = first_arg.__name__
                return f"{class_name}.{func_name}"

        # 检查是否是静态方法（通过函数的 __qualname__ 属性）
        if hasattr(func, '__qualname__') and '.' in func.__qualname__:
            # __qualname__ 格式为 "ClassName.method_name"
            qualname_parts = func.__qualname__.split('.')
            if len(qualname_parts) >= 2:
                # 取最后两部分：类名.方法名
                class_name = qualname_parts[-2]
                return f"{class_name}.{func_name}"

        # 如果不是类方法或实例方法，返回原函数名
        return func_name


# 全局日志记录器实例
_function_logger = FunctionLogger()


def log_function_calls(function_name_width: int = 30):
    """
    装饰器：自动记录函数调用日志

    Args:
        function_name_width: 函数名显示宽度，用于对齐（默认30以适应类名.方法名格式）

    Usage:
        @log_function_calls()
        def my_function(arg1, arg2="default"):
            return arg1 + arg2

        @log_function_calls(40)  # 自定义函数名宽度
        def another_function(x, y, z=None):
            return x * y
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 创建临时日志记录器（如果需要自定义宽度）
            if function_name_width != 30:
                logger = FunctionLogger(function_name_width)
                logger.log_function_call(func, args, kwargs)
            else:
                _function_logger.log_function_call(func, args, kwargs)

            # 执行原函数
            return func(*args, **kwargs)

        return wrapper
    return decorator


# 简化版装饰器，使用默认设置
def log_calls(func: Callable) -> Callable:
    """
    简化版装饰器：使用默认设置记录函数调用日志

    Usage:
        @log_calls
        def my_function(arg1, arg2="default"):
            return arg1 + arg2
    """
    return log_function_calls()(func)


# 模块级别的默认装饰器，直接使用模块名作为装饰器
def structlog_wrap(func: Callable) -> Callable:
    """
    模块默认装饰器：最简单的使用方式

    Usage:
        import structlog_wrap

        @structlog_wrap.structlog_wrap
        def my_function(arg1, arg2="default"):
            return arg1 + arg2

        # 或者
        from structlog_wrap import structlog_wrap

        @structlog_wrap
        def my_function(arg1, arg2="default"):
            return arg1 + arg2
    """
    return log_function_calls()(func)


# 让模块本身可以作为装饰器使用
class ModuleWrapper:
    """让模块本身可以作为装饰器使用的包装类"""

    def __init__(self, module):
        self._module = module

    def __call__(self, func: Callable) -> Callable:
        """当模块被用作装饰器时调用"""
        return log_function_calls()(func)

    def __getattr__(self, name):
        """代理模块的其他属性"""
        return getattr(self._module, name)


# 替换当前模块，使其可以直接作为装饰器使用
sys.modules[__name__] = ModuleWrapper(sys.modules[__name__])
