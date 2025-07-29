import logging
from queue import Queue
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
import multiprocessing

from PyMca5.PyMcaIO.ConfigDict import ConfigDict

from ... import h5_subprocess
from ...io.hdf5 import join_h5url

from ...xrffit import perform_batch_fit
from ...xrffit import outputbuffer_context
from ...xrffit import queue_outputbuffer_context

from ...xrffit.handlers import NexusOutputHandler
from ...xrffit.handlers import consume_handler_queue
from ...xrffit.handlers import stop_queue


logger = logging.getLogger(__name__)


def fit_single(
    bliss_scan_uri: str,
    xrf_spectra_uri_template: str,
    output_root_uri: str,
    process_uri_template: str,
    detector_name: str,
    config: Union[str, ConfigDict],
    energy: Optional[float] = None,
    quantification: Optional[dict] = None,
    energy_multiplier: Optional[float] = None,
    fast_fitting: bool = False,
    diagnostics: bool = False,
    figuresofmerit: Optional[bool] = None,
    **_,
) -> Tuple[str, str]:
    """Fitting of one scan with one detector.

    Returns the URL of the fit result and the URL to the NXentry group.
    """
    if figuresofmerit is None:
        figuresofmerit = diagnostics
    output_uri_template = join_h5url(output_root_uri, process_uri_template)
    output_root_uri = output_uri_template.format(detector_name)
    with outputbuffer_context(
        output_root_uri,
        diagnostics=diagnostics,
        figuresofmerit=figuresofmerit,
    ) as output_buffer:
        if output_buffer.already_existed:
            logger.warning("%s already exists", output_buffer.xrf_results_uri)
        else:
            xrf_spectra_uri = (
                f"{bliss_scan_uri}/{xrf_spectra_uri_template.format(detector_name)}"
            )
            perform_batch_fit(
                xrf_spectra_uris=[xrf_spectra_uri],
                cfg=config,
                output_buffer=output_buffer,
                energy=energy,
                energy_multiplier=energy_multiplier,
                quantification=quantification,
                fast=fast_fitting,
            )
        return output_buffer.xrf_results_uri, output_buffer.output_root_uri


def fit_multi(
    bliss_scan_uris: Sequence[str],
    xrf_spectra_uri_template: str,
    output_root_uri: str,
    process_uri_template: str,
    detector_names: Sequence[str],
    configs: Sequence[Union[str, ConfigDict]],
    energies: Optional[Sequence[Optional[float]]] = None,
    quantification: Optional[dict] = None,
    energy_multiplier: Optional[float] = None,
    fast_fitting: bool = False,
    diagnostics: bool = False,
    figuresofmerit: Optional[bool] = None,
    **_,
) -> Tuple[List[str], str]:
    """Parallelized fitting of a stack of identical scan with multiple detectors.

    Returns the URL's of the fit result (one URL per detector) and the URL to the NXentry group.
    """
    nscans = len(bliss_scan_uris)
    if energies:
        if len(energies) != nscans:
            raise ValueError(f"Requires {nscans} energies, one for each scan")
    else:
        energies = [None] * nscans
    ndetectors = len(detector_names)
    if len(configs) != ndetectors:
        raise ValueError(
            f"Requires {ndetectors} pymca configurations, one for each detector"
        )

    if figuresofmerit is None:
        figuresofmerit = diagnostics
    if diagnostics:
        default_group = "fit"
    else:
        default_group = "parameters"

    xrf_results_uris: List[str] = []
    next_output_root_uri: Optional[str] = None

    with ExitStack() as stack:
        mp_context = multiprocessing.get_context(method="spawn")
        ctx = mp_context.Manager()
        manager = stack.enter_context(ctx)
        queue = manager.Queue()

        ctx = ProcessPoolExecutor(
            mp_context=mp_context, initializer=h5_subprocess.initializer
        )
        executor = stack.enter_context(ctx)

        arguments: List[Tuple[tuple, dict, dict]] = list()
        output_handlers: Dict[int, NexusOutputHandler] = dict()
        queue_sendids: Set[int] = set()

        output_uri_template = join_h5url(output_root_uri, process_uri_template)
        output_uris = [
            output_uri_template.format(detector_name)
            for detector_name in detector_names
        ]
        if len(set(output_uris)) != len(output_uris):
            raise ValueError(
                "Add a place-holder '{}' for the detector name in the output URI template"
            )
        xrf_spectra_uris = [
            [
                f"{bliss_scan_uri}/{xrf_spectra_uri_template.format(detector_name)}"
                for bliss_scan_uri in bliss_scan_uris
            ]
            for detector_name in detector_names
        ]
        if len(set(xrf_spectra_uris[0])) != len(xrf_spectra_uris[0]):
            raise ValueError(
                "Add a place-holder '{}' for the detector name in the XRF spectra URI template"
            )

        for destinationid, (
            output_root_uri,
            detector_spectra_uris,
            config,
        ) in enumerate(zip(output_uris, xrf_spectra_uris, configs)):
            ctx = NexusOutputHandler(output_root_uri, default_group=default_group)
            output_handler = stack.enter_context(ctx)
            xrf_results_uris.append(output_handler.xrf_results_uri)
            next_output_root_uri = output_handler.output_root_uri
            if output_handler.already_existed:
                logger.warning("%s already exists", output_handler.xrf_results_uri)
                continue
            output_handlers[destinationid] = output_handler

            for i_scan, (xrf_spectra_uri, energy) in enumerate(
                zip(detector_spectra_uris, energies)
            ):
                queue_sendid = destinationid * nscans + i_scan
                queue_sendids.add(queue_sendid)

                buffer_args = (
                    queue,
                    queue_sendid,
                    destinationid,
                    nscans,
                    i_scan,
                )
                buffer_kwargs = {
                    "diagnostics": diagnostics,
                    "figuresofmerit": figuresofmerit,
                }
                fit_kwargs = {
                    "xrf_spectra_uris": [xrf_spectra_uri],
                    "cfg": config,
                    "energy": energy,
                    "energy_multiplier": energy_multiplier,
                    "quantification": quantification,
                    "fast": fast_fitting,
                }
                arguments.append(
                    (
                        _fit_main.__module__,
                        _fit_main.__name__,
                        buffer_args,
                        buffer_kwargs,
                        fit_kwargs,
                    )
                )

        if not arguments:
            return xrf_results_uris, next_output_root_uri

        # Sub-processes will send the fit results to the queue
        futures = {
            i: executor.submit(h5_subprocess.main, *args)
            for i, args in enumerate(arguments)
        }

        def raise_on_error():
            for i, future in list(futures.items()):
                if future.done():
                    future.result()  # re-raise exception (if any)
                    futures.pop(i)

        # Main process will receive results from the queue and save them in HDF5
        consume_handler_queue(output_handlers, queue, queue_sendids, raise_on_error)

        # Re-raise exceptions (if any)
        for future in futures.values():
            future.result()

    return xrf_results_uris, next_output_root_uri


def _fit_main(
    buffer_args: Tuple[Queue, int, int, Optional[int], int],
    buffer_kwargs: dict,
    fit_kwargs: dict,
) -> None:
    queue, sendid, destinationid, nscans, scan_index = buffer_args
    if nscans == 1:
        nscans = None
        scan_index = None
    try:
        with queue_outputbuffer_context(
            queue,
            sendid,
            destinationid,
            nscans=nscans,
            scan_index=scan_index,
            **buffer_kwargs,
        ) as output_buffer:
            perform_batch_fit(output_buffer=output_buffer, **fit_kwargs)
    finally:
        stop_queue(queue, sendid)
