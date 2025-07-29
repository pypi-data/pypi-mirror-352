"""
测试超长函数名的处理
"""
import structlog_wrap
from structlog_wrap import log_function_calls


@structlog_wrap
def short_name(x):
    """短函数名"""
    return x * 2


@structlog_wrap
def this_is_a_very_long_function_name_that_exceeds_the_default_width(x, y):
    """超长函数名，超过默认20字符宽度"""
    return x + y


@structlog_wrap
def extremely_long_function_name_that_definitely_exceeds_any_reasonable_width_setting(a, b, c):
    """极长函数名"""
    return a + b + c


@log_function_calls(15)  # 设置较小的宽度
def another_very_long_function_name(value):
    """用较小宽度测试超长函数名"""
    return value * 3


@log_function_calls(30)  # 设置较大的宽度
def medium_length_function_name(x, y):
    """中等长度函数名，用较大宽度测试"""
    return x - y


@log_function_calls(5)  # 设置很小的宽度
def test_tiny_width(x):
    """测试很小的宽度设置"""
    return x


if __name__ == "__main__":
    print("=== 测试超长函数名处理 ===\n")
    
    print("1. 默认宽度(20)下的各种函数名长度:")
    result1 = short_name(5)
    print(f"返回值: {result1}")
    
    result2 = this_is_a_very_long_function_name_that_exceeds_the_default_width(10, 20)
    print(f"返回值: {result2}")
    
    result3 = extremely_long_function_name_that_definitely_exceeds_any_reasonable_width_setting(1, 2, 3)
    print(f"返回值: {result3}\n")
    
    print("2. 自定义宽度下的函数名处理:")
    result4 = another_very_long_function_name(7)
    print(f"返回值: {result4}")
    
    result5 = medium_length_function_name(100, 30)
    print(f"返回值: {result5}")
    
    result6 = test_tiny_width(42)
    print(f"返回值: {result6}\n")
    
    print("✅ 测试完成！可以看到超长函数名被正确截断并保持对齐。")
