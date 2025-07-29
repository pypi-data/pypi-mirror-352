from typing import Optional
import numpy


def monitor_signal(
    expo_time: float,
    npoints: int,
    max_decay: float = 0.8,
    number_of_injections: int = 2,
    seed: Optional[int] = None,
):
    """Monitor signal between :math:``max_decay`` and :math:``1`` with
    a number of injections defined by :math:``number_of_injections``.
    """
    # All points in time at which we want the calculate the monitor signal.
    time = numpy.arange(npoints) * expo_time
    tmin = 0
    tmax = time[-1]

    # Fixed time distance between two injections.
    injection_period = (tmax - tmin) / number_of_injections

    # Fix intensity decay after each injection.
    decay = -numpy.log(max_decay) / injection_period

    # A single random injection time within the requested time range.
    tinjection0 = numpy.random.RandomState(seed=seed).uniform(tmin, tmax)

    # Calculate all other injection times from the singal random one, knowing
    # injections are `injection_period` apart in time between tmin and tmax.
    tinjections = [tinjection0]
    tinjection = tinjection0
    while tinjection > tmin:
        tinjection -= injection_period
        if tinjection >= tmin:
            tinjections.append(tinjection)
    tinjection = tinjection0
    while tinjection < tmax:
        tinjection += injection_period
        if tinjection <= tmax:
            tinjections.append(tinjection)

    # Add one injection before tmin and one injection after tmax.
    tinjections.append(max(tinjections) + injection_period)
    tinjections.append(min(tinjections) - injection_period)
    tinjections = sorted(tinjections)

    # Calculate the monitor intensity at all points in time
    # based on where each point is between two injections,
    # knowing the intensity decay after each injection.
    monitor = numpy.zeros(npoints)
    for t0, t1 in zip(tinjections[:-1], tinjections[1:]):
        idx = (time >= t0) & (time < t1)
        tperiod = time[idx] - t0
        monitor[idx] = numpy.exp(-decay * tperiod)
    return monitor
