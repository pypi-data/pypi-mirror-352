from ..math import rounding

import pytest


def test_round_to_significant():
    for m in [1, -1, 1e-3, 1e3]:
        assert rounding.round_to_significant(m * 99.99) == m * 100
        assert rounding.round_to_significant(m * 100.1) == m * 100
        assert rounding.round_to_significant(m * 100.9) == m * 101
        assert rounding.round_to_significant(m * 101) == m * 101
        assert rounding.round_to_significant(m * 1001) == m * 1000


def test_round_range():
    start, stop, step = 0, 1, 0.1
    start, stop, nbins = rounding.round_range(start, stop, step)
    assert start == 0
    assert stop == 1
    assert nbins == 10

    start, stop, step = 0, 1, 0.101
    start, stop, nbins = rounding.round_range(start, stop, step)
    assert start == pytest.approx(-0.005)
    assert stop == pytest.approx(1.005)
    assert nbins == 10

    start, stop, step = 0, 1, 0.099
    start, stop, nbins = rounding.round_range(start, stop, step)
    assert start == pytest.approx(0.005)
    assert stop == pytest.approx(0.995)
    assert nbins == 10
