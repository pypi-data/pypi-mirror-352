import math

from typing import Tuple


def round_to_significant(value: float, tolerance: float = 0.01) -> float:
    """
    Rounds a number to the least amount of significant decimals without
    changing the value by more than the given tolerance (default 1%).
    """
    if value == 0 or not math.isfinite(value):
        return value
    max_change = tolerance * abs(value)
    decimal_places = -int(math.floor(math.log10(max_change)))
    return round(value, decimal_places)


def round_range(start: float, stop: float, step: float) -> Tuple[float, float, int]:
    """
    Adjust the data range so that the number of bins is an integral number.

    :params start: minimum value
    :params stop: maximum value
    :param step: bin width
    :returns: minimum value, maximum value, number of bins
    """
    if step == 0 or not math.isfinite(start) or not math.isfinite(stop):
        return start, stop, 0
    data_range = stop - start
    nbins = int(round(abs(data_range / step)))
    rounded_range = nbins * step
    adjust = (rounded_range - data_range) / 2
    return start - adjust, stop + adjust, nbins
