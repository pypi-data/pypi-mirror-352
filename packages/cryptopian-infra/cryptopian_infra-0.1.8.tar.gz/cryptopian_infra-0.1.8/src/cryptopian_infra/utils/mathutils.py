import math
from decimal import Decimal


def to_decimal(num):
    try:
        return Decimal(str(num)) if not isinstance(num, Decimal) else num
    except Exception as e:
        raise ValueError(f"Cannot convert {num} to Decimal: {e}")


def normalize_fraction(d):
    normalized = d.normalize()
    sign, digits, exponent = normalized.as_tuple()
    if exponent > 0:
        return Decimal((sign, digits + (0,) * exponent, 0))
    else:
        return normalized


def floor(num, precision):
    num = to_decimal(num)
    factor = to_decimal(pow(10, precision))
    return math.floor(num * factor) / factor


def floor_to_nearest(num, precision):
    factor = 1 / to_decimal(precision)
    return math.floor(num * factor) / factor


def ceil(num, precision):
    num = to_decimal(num)
    factor = to_decimal(pow(10, precision))
    return math.ceil(num * factor) / factor


def ceil_to_nearest(num, precision):
    factor = 1 / to_decimal(precision)
    return math.ceil(num * factor) / factor


def round_to_nearest(number, precision):
    # Calculate the rounding factor based on precision
    factor = 1 / to_decimal(precision)

    # Round the number to the nearest precision
    rounded_number = round(number * factor) / factor
    return rounded_number


def extract_dp(num):
    num_str = str(num)
    index_dot = num_str.index('.')
    if index_dot < 0:
        return -1 * (len(num_str) - 1)
    index_1 = num_str.index('1')
    if index_1 > index_dot:
        return index_1 - index_dot
    else:
        return index_1 - index_dot + 1


def format_decimal(num: Decimal):
    result = str(num)
    if 'E' in result or 'e' in result:
        result = f'{num:.{abs(num.as_tuple().exponent)}f}'
    return result
