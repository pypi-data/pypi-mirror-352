import json
from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.bindings import ow_build_opts
from ewoksorange.gui.parameterform import ParameterForm

from ewoksfluo.io.hdf5 import split_h5uri
from ewoksfluo.gui.data_viewer import DataViewer
from ewoksfluo.tasks.sum_detectors import sum_spectra


__all__ = ["OWSumXrfSpectra"]


class OWSumXrfSpectra(
    OWEwoksWidgetOneThread, **ow_build_opts, ewokstaskclass=sum_spectra.SumXrfSpectra
):
    name = "Sum Spectra"
    description = "Add single-scan XRF spectra from multiple detectors"

    def __init__(self):
        super().__init__()
        self._init_control_area()
        self._init_main_area()

    def _init_control_area(self):
        super()._init_control_area()
        self._default_inputs_form = ParameterForm(parent=self.controlArea)
        defaults = {
            **sum_spectra.DEFAULTS,
            "output_root_uri": "processed_data.h5",
        }
        values = self.get_default_input_values(include_missing=True, defaults=defaults)

        parameters = {
            "bliss_scan_uri": {
                "label": "Scan URI",
                "value_for_type": "",
                "select": "h5group",
            },
            "detector_names": {
                "label": "List of detectors to sum",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
            },
            "xrf_spectra_uri_template": {
                "label": "XRF spectra URI template",
                "value_for_type": "",
            },
            "detector_normalization_template": {
                "label": "Detector weight formula",
                "value_for_type": "",
            },
            "output_root_uri": {
                "label": "HDF5 output filename",
                "value_for_type": "",
                "select": "h5group",
            },
        }

        for name, kw in parameters.items():
            self._default_inputs_form.addParameter(
                name,
                value=values[name],
                value_change_callback=self._default_inputs_changed,
                **kw,
            )

    def _default_inputs_changed(self):
        self.update_default_inputs(**self._default_inputs_form.get_parameter_values())
        self._update_input_data()
        self._update_output_data()

    def handleNewSignals(self) -> None:
        self._update_input_data()
        super().handleNewSignals()

    def task_output_changed(self):
        self._update_output_data()

    def _init_main_area(self):
        super()._init_main_area()
        layout = self._get_main_layout()

        self._viewer = DataViewer(parent=self.mainArea)
        self._viewer.setVisible(True)
        layout.addWidget(self._viewer)
        layout.setStretchFactor(self._viewer, 1)

        self._update_output_data()

    def _update_input_data(self):
        dynamic = self.get_dynamic_input_names()
        for name in self.get_input_names():
            self._default_inputs_form.set_parameter_enabled(name, name not in dynamic)

    def _update_output_data(self):
        self._refresh_output_file()

    def _refresh_output_file(self):
        uri = self.get_task_output_value("bliss_scan_uri")
        if uri:
            self._viewer.updateFile(split_h5uri(uri)[0])
