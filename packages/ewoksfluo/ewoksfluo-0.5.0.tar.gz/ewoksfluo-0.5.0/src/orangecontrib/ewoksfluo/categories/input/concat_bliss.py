import json

from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.bindings import ow_build_opts
from ewoksorange.gui.parameterform import ParameterForm

from ewoksfluo.io.hdf5 import split_h5uri
from ewoksfluo.gui.data_viewer import DataViewer
from ewoksfluo.tasks.input.concat_bliss import ConcatBliss

__all__ = ["OWConcatBliss"]


class OWConcatBliss(
    OWEwoksWidgetOneThread, **ow_build_opts, ewokstaskclass=ConcatBliss
):
    name = "Concat BLISS scans"
    description = "Concatenate BLISS scans"

    def __init__(self):
        super().__init__()
        self._init_control_area()
        self._init_main_area()

    def _init_control_area(self):
        super()._init_control_area()
        self._default_inputs_form = ParameterForm(parent=self.controlArea)
        defaults = {"output_root_uri": "concat_data.h5"}
        values = self.get_default_input_values(include_missing=True, defaults=defaults)

        parameters = {
            "bliss_scan_uris": {
                "label": "Bliss scans",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
            },
            "bliss_scan_uri": {
                "label": "Concatenated Bliss scan",
                "value_for_type": "",
                "select": "h5group",
            },
            "virtual_axes": {
                "label": "Virtual axes",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
            },
            "axes_units": {
                "label": "Axes units",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
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
        uri = self.get_task_input_value("output_root_uri")
        if uri:
            self._viewer.updateFile(split_h5uri(uri)[0])
