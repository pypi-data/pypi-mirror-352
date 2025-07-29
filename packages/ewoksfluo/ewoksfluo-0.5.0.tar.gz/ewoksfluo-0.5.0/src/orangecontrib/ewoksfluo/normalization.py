import json

from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.bindings import ow_build_opts
from ewoksorange.gui.parameterform import ParameterForm

from ewoksfluo.tasks.normalization import Normalization
from ewoksfluo.gui.data_viewer import DataViewer
from ewoksfluo.io.hdf5 import split_h5uri


__all__ = ["OWNormalization"]


class OWNormalization(
    OWEwoksWidgetOneThread, **ow_build_opts, ewokstaskclass=Normalization
):
    name = "Normalization"
    description = "Normalize data (spectra or fit results)"

    def __init__(self):
        super().__init__()
        self._init_control_area()
        self._init_main_area()

    def _init_control_area(self):
        super()._init_control_area()
        self._default_inputs_form = ParameterForm(parent=self.controlArea)
        values = self.get_default_input_values(include_missing=True)

        parameters = {
            "data_uri": {
                "label": "Data URI to be normalized",
                "value_for_type": "",
                "select": "h5group",
            },
            "normalize_uris": {
                "label": "URIs to normalization data",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
            },
            "bliss_scan_uri": {
                "label": "Scan URI used in normalization",
                "value_for_type": "",
                "select": "h5group",
            },
            "expression_template": {
                "label": "Normalization formula",
                "value_for_type": "",
            },
            "output_root_uri": {
                "label": "HDF5 output URI",
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
        uri = self.get_task_output_value("corr_data_uri")
        if uri:
            self._viewer.updateFile(split_h5uri(uri)[0])
