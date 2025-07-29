"""
测试最简单的使用方式：直接 import structlog_wrap 然后 @structlog_wrap
"""
import structlog_wrap


@structlog_wrap
def simple_add(a, b):
    """简单的加法函数"""
    return a + b


@structlog_wrap
def greet(name: str, greeting: str = "Hello"):
    """问候函数"""
    return f"{greeting}, {name}!"


@structlog_wrap
def process_list(items: list, multiplier: int = 2, reverse: bool = False):
    """处理列表"""
    result = [x * multiplier for x in items]
    if reverse:
        result.reverse()
    return result


@structlog_wrap
def complex_function(user_id: int, config: dict, **kwargs):
    """复杂函数示例"""
    return {
        "user_id": user_id,
        "config_keys": list(config.keys()),
        "extra": kwargs
    }



if __name__ == "__main__":
    print("=== 最简单的 structlog_wrap 使用方式演示 ===\n")
    
    print("1. 简单函数调用:")
    result1 = simple_add(10, 20)
    print(f"返回值: {result1}\n")
    
    print("2. 带默认参数的函数:")
    result2 = greet("张三")
    print(f"返回值: {result2}")
    
    result3 = greet("李四", "Hi")
    print(f"返回值: {result3}\n")
    
    print("3. 处理列表数据:")
    test_data = [1, 2, 3, 4, 5]
    result4 = process_list(test_data)
    print(f"返回值: {result4}")
    
    result5 = process_list(test_data, multiplier=3, reverse=True)
    print(f"返回值: {result5}\n")
    
    print("4. 复杂函数调用:")
    config = {"theme": "dark", "lang": "zh"}
    result6 = complex_function(
        user_id=12345,
        config=config,
        debug=True,
        version="1.0"
    )
    print(f"返回值: {result6}\n")
    
    print("5. 测试长参数:")
    long_list = list(range(50))
    result7 = process_list(long_list, 2)
    print(f"返回值长度: {len(result7)}")


    print("6. 测试 超长函数名称:")
    @structlog_wrap
    def very_long_function_name_1234567890_abcdefghijklmnopqrstuvwxyz(a):
        """超长函数名称"""
        return a
    
    result8 = very_long_function_name_1234567890_abcdefghijklmnopqrstuvwxyz(10)
    print(f"返回值: {result8}")