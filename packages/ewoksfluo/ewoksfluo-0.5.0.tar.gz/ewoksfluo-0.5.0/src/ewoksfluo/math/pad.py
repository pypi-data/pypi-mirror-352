import numbers
from typing import Tuple, Dict, Any, Optional, Sequence

import h5py
import numpy


def pad_length(*all_arrays: Tuple[Dict[str, Any]]) -> Optional[int]:
    """Return the length to which all arrays should be padded to be the same size.
    Returns None if all arrays already have the same size or no arrays are found.
    """
    lengths = set()

    for arrays in all_arrays:
        for value in arrays.values():
            if _is_number_array(value):
                lengths.add(len(value))

    if len(lengths) > 1:
        return max(lengths)
    else:
        return None


def pad_arrays(max_len: int, *all_arrays: Tuple[Dict[str, Any]]) -> None:
    """Pad all sequence-like values in all dictionaries to the specified max_len with nan."""
    for arrays in all_arrays:
        for key, value in arrays.items():
            if _is_number_array(value):
                pad_array[key] = pad_array(pad_array[key], max_len)


def pad_array(value: Sequence, max_len: int) -> Sequence:
    """Pad array when the length is smaller than max_len."""
    nextra = max_len - len(value)
    if nextra <= 0:
        return value
    arr = numpy.asarray(value, dtype=float)
    pad_width = [(0, nextra)] + [(0, 0)] * (arr.ndim - 1)
    return numpy.pad(arr, pad_width, mode="constant", constant_values=numpy.nan)


def _is_number_array(value: Any) -> bool:
    if isinstance(value, (h5py.Dataset, numpy.ndarray)):
        return numpy.issubdtype(value.dtype, numpy.number)
    if isinstance(value, Sequence) and value:
        return isinstance(value[0], numbers.Number)
    return False
