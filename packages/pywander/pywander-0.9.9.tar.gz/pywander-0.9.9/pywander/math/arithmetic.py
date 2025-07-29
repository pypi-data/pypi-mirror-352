import math
from typing import Union

from pywander.exceptions import OutOfChoiceError, NotIntegerError, OutOfRangeError

def is_divisible(a, b):
    """
    a 是否被 b 整除
    """
    if (not isinstance(a, int)) or (not isinstance(b, int)):
        raise NotIntegerError

    if a % b == 0:
        return True
    else:
        return False


def is_even(n):
    """is this number is even, required n is an integer.

    >>> is_even(0)
    True
    >>> is_even(-1)
    False
    >>> is_even(-2)
    True

    """
    if not isinstance(n, int):
        raise NotIntegerError

    if n % 2 == 0:
        return True
    else:
        return False


def is_odd(n):
    """is this number is odd, required n is an integer."""
    return not is_even(n)


def round_half_up(n, decimals=0):
    """
    实现常见的那种四舍五入，警告这只是一种近似，如果有精确的小数需求还是推荐使用decimal模块。
    """
    multiplier = 10 ** decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def radix_conversion(number: Union[int, str], output_radix, input_radix=10) -> str:
    """
    数字进制转换函数

    number: input can be a number or string
    output_radix:
    input_radix: the input number radix, default is 10

    the radix support list: ['bin', 'oct', 'dec', 'hex', 2, 8, 10, 16]

>>> radix_conversion(10, 'bin')
'1010'
>>> radix_conversion('0xff', 2, 16)
'11111111'
>>> radix_conversion(0o77, 'hex')
'3f'
>>> radix_conversion(100, 10)
'100'
>>> radix_conversion(100,1)
Traceback (most recent call last):
......
pywander.exceptions.OutOfChoiceError: radix is out of choice.

    """
    name_map = {'bin': 2, 'oct': 8, 'dec': 10, 'hex': 16}

    for index, radix in enumerate([input_radix, output_radix]):
        if radix is None:
            continue

        if radix not in ['bin', 'oct', 'dec', 'hex', 2, 8, 10, 16]:
            raise OutOfChoiceError("radix is out of choice.")

        if radix in name_map.keys():
            if index == 0:
                input_radix = name_map[radix]
            elif index == 1:
                output_radix = name_map[radix]

    if isinstance(number, str) and input_radix:
        number = int(number, input_radix)

    if output_radix == 2:
        return f'{number:b}'
    elif output_radix == 8:
        return f'{number:o}'
    elif output_radix == 10:
        return f'{number:d}'
    elif output_radix == 16:
        return f'{number:x}'
    else:
        raise OutOfChoiceError(f'wrong radix {output_radix}')


def is_prime(n):
    """test input integer n is a prime.
    >>> is_prime(5)
    True
    >>> is_prime(123)
    False

    """
    if not isinstance(n, int):
        raise NotIntegerError
    if n<=1:
        raise OutOfRangeError("prime need greater than 1")

    if n == 2:
        return True
    elif n < 2 or not n & 1:
        return False
    for x in range(3, int(n ** 0.5) + 1, 2):
        if n % x == 0:
            return False
    return True


def gen_prime(n):
    """generate n prime"""
    count = 0
    x = 2
    while count < n:
        if is_prime(x):
            count += 1
            yield x
        x += 1


def gen_prime2(n):
    """generate prime smaller than n"""
    for x in range(2, n):
        if is_prime(x):
            yield x


def last_gen(genobj):
    """
    get the last element of the generator
    :param genobj:
    :return:
    """
    return list(genobj)[-1]


def prime(n):
    """get the nth prime"""
    if n <= 0:
        raise OutOfRangeError("第零个或者第负数个素数？")
    else:
        return last_gen(gen_prime(n))


def gen_fibonacci(n):
    """generate fibonacci number"""
    if not isinstance(n, int):
        raise NotIntegerError

    count = 0
    a, b = 0, 1

    while count < n:
        a, b = b, a + b
        yield a
        count += 1


def fibonacci(n):
    """get nth fibonacci number"""
    if n <= 0:
        raise OutOfRangeError("没有零个或小于零个斐波那契数的概念那。")
    else:
        return last_gen(gen_fibonacci(n))


def factorial(n):
    """factorial n!"""
    return math.factorial(n)

def gcd(*integers):
    """
    最大公约数
    """
    return math.gcd(*integers)


def lcm(*integers):
    """
    最小公倍数
    """
    return math.lcm(*integers)

def get_leading_digit_and_magnitude(num):
    """
    获取浮点数的第一位有效数字和其数量级

    参数:
        num (float): 输入的浮点数

    返回:
        tuple: (第一位有效数字, 数量级)
    """
    if num == 0:
        return (0, 0)

    # 处理负数
    num = abs(num)

    # 计算数量级（10的幂）
    magnitude = math.floor(math.log10(num))

    # 计算第一位有效数字
    leading_digit = int(num / (10 ** magnitude))

    return (leading_digit, magnitude)


class Interval:
    def __init__(self, lower, upper, include_lower=True, include_upper=True):
        self.lower = lower
        self.upper = upper
        self.include_lower = include_lower
        self.include_upper = include_upper

    def __contains__(self, number):
        """使区间对象支持 'in' 操作符"""
        left = self.lower <= number if self.include_lower else self.lower < number
        right = number <= self.upper if self.include_upper else number < self.upper
        return left and right

def calc_approximate_range(a, epi_digit, epi_mag):
    epi = epi_digit * 10 ** epi_mag
    return a - epi, a + epi

def get_approximate_number(a, A):
    """
    a 给定的待修正的近似数
    A 准确数
    """
    digit, mag = get_leading_digit_and_magnitude(a)

    epi_digit = 99
    epi_mag = mag - 1

    # 最小mag确定
    approximate_range = calc_approximate_range(a, epi_digit, epi_mag)
    while A in Interval(*approximate_range):
        epi_mag = epi_mag - 1
        approximate_range = calc_approximate_range(a, epi_digit, epi_mag)
    epi_mag = epi_mag + 1

    # 最小digit确定
    approximate_range = calc_approximate_range(a, epi_digit, epi_mag)
    while A in Interval(*approximate_range):
        epi_digit = epi_digit - 1
        approximate_range = calc_approximate_range(a, epi_digit, epi_mag)
    epi_digit = epi_digit + 1

    print(format_float(epi_digit, epi_mag))
    return epi_digit, epi_mag


def format_float(digit, mag):
    """
    根据digit整数和mag指数来输出小数
    """
    # 计算并格式化为小数形式
    result = digit * (10 ** mag)
    formatted = f"{result:.{abs(mag)}f}"  # 根据指数确定小数位数
    return formatted


