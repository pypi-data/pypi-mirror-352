from typing import Optional, Sequence, Union, Tuple, List, Dict

from PyMca5.PyMcaIO import ConfigDict
from PyMca5.PyMcaIO import HDF5Stack1D
from PyMca5.PyMcaPhysics.xrf import FastXRFLinearFit
from PyMca5.PyMcaPhysics.xrf import McaAdvancedFitBatch

from .config import adapt_pymca_config, temp_config_filename
from ewoksfluo.io.hdf5 import split_h5uri


def perform_batch_fit(
    xrf_spectra_uris: Sequence[str],
    cfg: Union[str, ConfigDict.ConfigDict],
    output_buffer,
    energy: Optional[float] = None,
    energy_multiplier: Optional[float] = None,
    mlines: Optional[dict] = None,
    quantification: Optional[dict] = None,
    fast: bool = False,
) -> None:
    """Fit XRF spectra in batch with one primary beam energy. Least-square fitting.
    If you intend a linear fit, modify the configuration:

        - Get current energy calibration with "Load From Fit"
        - Enable: Perform a Linear Fit
        - Disable: Stripping
        - Strip iterations = 0

    Fast linear least squares:

          - Use SNIP instead of STRIP

    :param xrf_spectra_uris: spectra to fit.
    :param cfg: configuration file to use.
    :param output_buffer: object that receives the fit results.
    :param energy: primary beam energy. Defaults to None.
    :param mlines: elements (keys) which M line group must be replaced by some M subgroups (values). Defaults to None.
    :param quantification: save massfractions. Defaults to False.
    :param fast: use SNIP instead of STRIP. Defaults to False.
    :param diagnostics: fit model and residuals. Defaults to False.
    :param figuresofmerit: chi-square value and other figures of merit. Defaults to False.
    :param energy_multiplier: adds a higher energy bound equal to energy*energy_multiplier to include high-energy peaks. Default: no bound is added.
    :raises ValueError: if all paths in filelist do not have the same HDF5 group as parent.
    """
    if not cfg:
        raise RuntimeError("PyMca configuration is empty")
    if isinstance(cfg, str):
        cfg_file = cfg
        cfg = ConfigDict.ConfigDict(filelist=[cfg_file])
        if not cfg:
            raise RuntimeError(
                f"PyMca configuration could not be read or is empty: {cfg_file!r}"
            )

    adapt_pymca_config(
        cfg,
        energy,
        mlines=mlines,
        quant=quantification,
        fast=fast,
        energy_multiplier=energy_multiplier,
    )

    filelist, selection, scanlist = _parse_hdf5_uris(xrf_spectra_uris)
    if fast:
        batch = FastXRFLinearFit.FastXRFLinearFit()
        stack = HDF5Stack1D.HDF5Stack1D(filelist, selection, scanlist=scanlist)
        kwargs = {
            "y": stack,
            "configuration": cfg,
            "concentrations": bool(quantification),
            "refit": 0,  # the ewoksfluo output buffer cannot handle it
            "outbuffer": output_buffer,
        }
        with output_buffer.saveContext():
            batch.fitMultipleSpectra(**kwargs)
    else:
        selection["entry"] = scanlist
        kwargs = {
            "filelist": filelist,
            "selection": selection,
            "concentrations": bool(quantification),
            "fitfiles": 0,
            "fitconcfile": 0,
            "outbuffer": output_buffer,
        }
        with temp_config_filename(cfg) as cfgfilename:
            batch = McaAdvancedFitBatch.McaAdvancedFitBatch(cfgfilename, **kwargs)
            with output_buffer.saveContext():
                batch.processList()


def _parse_hdf5_uris(
    uris: Sequence[str],
) -> Tuple[List[str], Dict[str, List[str]], List[str]]:
    split_results = list(zip(*(split_h5uri(uri) for uri in uris)))
    filelist, datasetlist = split_results
    filelist = list(set(filelist))
    if len(filelist) != 1:
        raise ValueError("cannot handle scans in different files")
    entries, datasets = zip(*(_parse_hdf5_dataset(dataset) for dataset in datasetlist))
    datasets = list(set(datasets))
    if len(datasets) != 1:
        raise ValueError("dataset location is each scan must be the same for all scans")
    selection = {"y": datasets[0]}
    scanlist = list(entries)
    return filelist, selection, scanlist


def _parse_hdf5_dataset(dataset: str) -> Tuple[str, str]:
    parts = [s for s in dataset.split("/") if s]
    return parts[0], "/" + "/".join(parts[1:])
