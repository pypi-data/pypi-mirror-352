import json

from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.bindings import ow_build_opts
from ewoksorange.gui.parameterform import ParameterForm

from ewoksfluo.tasks.input.spec_to_bliss import SpecToBliss
from ewoksfluo.gui.data_viewer import DataViewer


__all__ = ["OWSpecToBliss"]


class OWSpecToBliss(
    OWEwoksWidgetOneThread, **ow_build_opts, ewokstaskclass=SpecToBliss
):
    name = "SPEC to BLISS"
    description = "Convert SPEC data to BLISS data"

    def __init__(self):
        super().__init__()
        self._init_control_area()
        self._init_main_area()

    def _init_control_area(self):
        super()._init_control_area()
        self._default_inputs_form = ParameterForm(parent=self.controlArea)
        values = self.get_default_input_values(include_missing=True)

        parameters = {
            "input_filename": {
                "label": "Spec filename",
                "value_for_type": "",
                "select": "file",
            },
            "output_filename": {
                "label": "HDF5 filename",
                "value_for_type": "",
                "select": "file",
            },
            "scan_numbers": {
                "label": "Scan numbers",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
            },
            "subscan_numbers": {
                "label": "Sub-scan numbers",
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
        filename = self.get_task_input_value("output_filename")
        if filename:
            self._viewer.updateFile(filename)
