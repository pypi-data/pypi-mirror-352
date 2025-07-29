"""
使用示例：演示structlog_wrap装饰器的用法
"""
from structlog_wrap import log_function_calls, log_calls


@log_calls
def simple_function(name: str, age: int = 25):
    """简单函数示例"""
    return f"Hello, {name}! You are {age} years old."


@log_function_calls(30)  # 自定义函数名宽度为30
def calculate_area(length: float, width: float, unit: str = "m"):
    """计算面积"""
    area = length * width
    return f"{area} {unit}²"


@log_calls
def process_data(data: list, multiplier: int = 2, debug: bool = False):
    """处理数据"""
    if debug:
        print(f"Processing {len(data)} items")
    return [x * multiplier for x in data]


@log_function_calls(25)
def complex_function(
    user_id: int,
    settings: dict,
    options: list = None,
    callback=None,
    **extra_params
):
    """复杂函数示例，包含多种参数类型"""
    if options is None:
        options = []
    
    result = {
        "user_id": user_id,
        "settings_count": len(settings),
        "options_count": len(options),
        "extra_params": extra_params
    }
    
    if callback:
        callback(result)
    
    return result


def demo_callback(result):
    """回调函数示例"""
    print(f"Callback received: {result}")


if __name__ == "__main__":
    print("=== structlog_wrap 装饰器演示 ===\n")
    
    # 简单函数调用
    print("1. 简单函数调用:")
    result1 = simple_function("张三")
    print(f"返回值: {result1}\n")
    
    result2 = simple_function("李四", 30)
    print(f"返回值: {result2}\n")
    
    # 带自定义宽度的函数
    print("2. 自定义函数名宽度:")
    result3 = calculate_area(10.5, 8.2)
    print(f"返回值: {result3}\n")
    
    result4 = calculate_area(5.0, 3.0, "cm")
    print(f"返回值: {result4}\n")
    
    # 处理列表数据
    print("3. 处理数据:")
    test_data = [1, 2, 3, 4, 5]
    result5 = process_data(test_data)
    print(f"返回值: {result5}\n")
    
    result6 = process_data(test_data, multiplier=3, debug=True)
    print(f"返回值: {result6}\n")
    
    # 复杂函数调用
    print("4. 复杂函数调用:")
    settings = {"theme": "dark", "language": "zh-CN", "notifications": True}
    options = ["option1", "option2", "option3"]
    
    result7 = complex_function(
        user_id=12345,
        settings=settings,
        options=options,
        callback=demo_callback,
        extra_param1="value1",
        extra_param2=42
    )
    print(f"返回值: {result7}\n")
    
    # 测试长字符串参数
    print("5. 长字符串参数测试:")
    long_string = "这是一个很长的字符串，用来测试参数值过长时的截断功能。" * 3
    result8 = simple_function(long_string, 25)
    print(f"返回值长度: {len(result8)}\n")
