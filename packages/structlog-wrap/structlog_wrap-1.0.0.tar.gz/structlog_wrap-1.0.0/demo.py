"""
最简单的 structlog_wrap 使用演示
只需要 import structlog_wrap，然后用 @structlog_wrap 装饰函数即可
"""
import structlog_wrap


@structlog_wrap
def add(a, b):
    """简单的加法函数"""
    return a + b


@structlog_wrap
def greet(name, greeting="Hello"):
    """问候函数，带默认参数"""
    return f"{greeting}, {name}!"


@structlog_wrap
def calculate(x, y, operation="add"):
    """计算函数，演示多种参数类型"""
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y
    else:
        return None


if __name__ == "__main__":
    print("=== structlog_wrap 最简单用法演示 ===\n")
    
    # 基本函数调用
    result1 = add(5, 3)
    print(f"5 + 3 = {result1}\n")
    
    # 带默认参数的函数
    result2 = greet("世界")
    print(f"问候: {result2}")
    
    result3 = greet("Python", "Hi")
    print(f"问候: {result3}\n")
    
    # 多参数函数
    result4 = calculate(10, 20)
    print(f"10 + 20 = {result4}")
    
    result5 = calculate(10, 20, "multiply")
    print(f"10 * 20 = {result5}")
    
    print("\n✅ 完成！只需要 import structlog_wrap 然后 @structlog_wrap 即可自动记录函数调用日志！")
