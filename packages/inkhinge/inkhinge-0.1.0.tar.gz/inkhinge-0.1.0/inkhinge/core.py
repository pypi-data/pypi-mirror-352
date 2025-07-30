"""inkhinge包的核心功能模块"""


def add_numbers(a: int | float, b: int | float) -> int | float:
    """
    将两个数字相加的简单函数

    参数:
        a (int|float): 第一个数字
        b (int|float): 第二个数字

    返回:
        int|float: 两个数字的和

    示例:
        >>> add_numbers(1, 2)
        3
        >>> add_numbers(1.5, 2.5)
        4.0
    """
    return a + b


def multiply_numbers(a: int | float, b: int | float) -> int | float:
    """
    将两个数字相乘的简单函数

    参数:
        a (int|float): 第一个数字
        b (int|float): 第二个数字

    返回:
        int|float: 两个数字的乘积

    示例:
        >>> multiply_numbers(2, 3)
        6
        >>> multiply_numbers(2.5, 3)
        7.5
    """
    return a * b