from typing import Dict, Optional
import numpy
from numpy.typing import DTypeLike


def apply_extendable_deadtime(
    photons,
    elapsed_time,
    max_dt_percentage,
    integral_type: Optional[DTypeLike] = numpy.uint32,
):
    """Number of counts measured by a digital signal processor with extendable a.k.a. paralyzable
    deadtime for a given number of incoming photons."""
    r = photons / elapsed_time
    max_r = r.max()
    tau = -numpy.log(1 - max_dt_percentage / 100) / max_r
    dt = 1 - numpy.exp(-tau * photons / elapsed_time)
    measured = photons * (1 - dt)
    if integral_type is None:
        return measured
    return (measured + 0.5).astype(integral_type)


def apply_dualchannel_signal_processing(
    spectra: numpy.ndarray,
    max_dt_fast=0.1,
    max_dt_slow=20,
    elapsed_time=0.1,
    counting_noise: bool = True,
    integral_type: Optional[DTypeLike] = numpy.uint32,
) -> Dict[str, numpy.ndarray]:
    """MCA spectra with statistics measured by a dual-channel digital signal processor:
    one channel with low deadtime and low energy precision and
    one channel with high deadtime and high energy precision.

    The last dimension of `spectra` is the MCA channel/energy dimension.
    An MCA spectrum (multi-channel analyzer) contains measured photons binned
    by their energy.
    """
    shape = spectra.shape[:-1]
    if integral_type:
        spectra = spectra.astype(integral_type)
    if counting_noise:
        spectra = numpy.random.poisson(spectra)
    photons = spectra.sum(axis=-1)
    elapsed_time = numpy.full(shape, elapsed_time)
    events = apply_extendable_deadtime(
        photons, elapsed_time, max_dt_slow, integral_type
    )
    triggers = apply_extendable_deadtime(photons, elapsed_time, max_dt_fast)
    fractional_dead_time = 1 - events / photons
    event_count_rate = events / elapsed_time
    trigger_live_time = elapsed_time * triggers / photons
    live_time = elapsed_time * events / photons
    trigger_count_rate = triggers / trigger_live_time
    spectra = spectra * (events / photons)[..., numpy.newaxis]
    if integral_type:
        spectra = spectra.astype(integral_type)
    return {
        "spectrum": spectra,
        "events": events,
        "triggers": triggers,
        "event_count_rate": event_count_rate,
        "trigger_count_rate": trigger_count_rate,
        "live_time": live_time,
        "trigger_live_time": trigger_live_time,
        "elapsed_time": elapsed_time,
        "fractional_dead_time": fractional_dead_time,
    }
