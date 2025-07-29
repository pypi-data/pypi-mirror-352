import numpy
from ewoksfluo.tasks.example_data.deadtime import apply_dualchannel_signal_processing


def test_apply_dualchannel_signal_processing():
    for _ in range(5):
        measured = apply_dualchannel_signal_processing(
            numpy.array([[10000]]), elapsed_time=1.0
        )
        counts = measured["spectrum"] / measured["live_time"] * 0.1
        if counts[0, 0] != 10000:
            break
    else:
        assert counts[0, 0] != 10000

    measured = apply_dualchannel_signal_processing(
        numpy.array([[10000.1]]),
        elapsed_time=0.1,
        counting_noise=False,
        integral_type=numpy.uint32,
    )
    counts = measured["spectrum"] / measured["live_time"] * 0.1
    assert counts[0, 0] == 10000

    measured = apply_dualchannel_signal_processing(
        numpy.array([[10000.1]]),
        elapsed_time=0.1,
        counting_noise=False,
        integral_type=None,
    )
    counts = measured["spectrum"] / measured["live_time"] * 0.1
    numpy.testing.assert_almost_equal(counts[0, 0], 10000.1, decimal=9)
