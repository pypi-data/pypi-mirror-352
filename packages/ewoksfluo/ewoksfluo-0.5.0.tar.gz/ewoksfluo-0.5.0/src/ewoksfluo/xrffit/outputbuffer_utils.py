from multiprocessing import Queue
from typing import Optional
from contextlib import contextmanager

from .handlers import NexusOutputHandler
from .handlers import QueueOutputHandler
from .buffers import PyMcaOutputBuffer
from .buffers import ExternalOutputBuffer


@contextmanager
def queue_outputbuffer_context(
    queue: Queue,
    sendid: int,
    destinationid: int,
    nscans: Optional[int] = None,
    scan_index: Optional[int] = None,
    diagnostics: bool = False,
    figuresofmerit: bool = True,
):
    with QueueOutputHandler(
        queue, sendid, destinationid, nscans, scan_index
    ) as handler:
        yield ExternalOutputBuffer(
            handler, diagnostics=diagnostics, figuresofmerit=figuresofmerit
        )


@contextmanager
def outputbuffer_context(
    output_root_uri: str,
    diagnostics: bool = False,
    figuresofmerit: bool = True,
    output_handler: str = "nexus",
    open_options: Optional[dict] = None,
):
    if open_options is None:
        open_options = {}

    if output_handler == "nexus":
        if diagnostics:
            default_group = "fit"
        else:
            default_group = "parameters"
        with NexusOutputHandler(
            output_root_uri, default_group=default_group, **open_options
        ) as handler:
            yield ExternalOutputBuffer(
                handler, diagnostics=diagnostics, figuresofmerit=figuresofmerit
            )
    elif output_handler == "pymca":
        # Handler and buffer are coupled
        yield PyMcaOutputBuffer(
            output_root_uri,
            diagnostics=diagnostics,
            figuresofmerit=figuresofmerit,
            **open_options,
        )
    else:
        raise ValueError(f"Unknown output handler {output_handler}")
