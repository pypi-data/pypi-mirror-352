from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.bindings import ow_build_opts
from ewoksorange.gui.parameterform import ParameterForm

from ewoksfluo.tasks.input.pick_scan import PickScan
from ewoksfluo.gui.data_viewer import DataViewer


__all__ = ["OWPickScan"]


class OWPickScan(OWEwoksWidgetOneThread, **ow_build_opts, ewokstaskclass=PickScan):
    name = "Pick scan"
    description = "Pick scan"

    def __init__(self):
        super().__init__()
        self._init_control_area()
        self._init_main_area()
        self._refresh_input_file()

    def _init_control_area(self):
        super()._init_control_area()
        self._default_inputs_form = ParameterForm(parent=self.controlArea)
        values = self.get_default_input_values(include_missing=True)

        parameters = {
            "filename": {
                "label": "HDF5 file name",
                "value_for_type": "",
                "select": "file",
            },
            "scan_number": {
                "label": "Scan number",
                "value_for_type": 0,
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

    def handleNewSignals(self) -> None:
        self._update_input_data()
        super().handleNewSignals()

    def _init_main_area(self):
        super()._init_main_area()
        layout = self._get_main_layout()

        self._viewer = DataViewer(parent=self.mainArea)
        self._viewer.setVisible(True)
        layout.addWidget(self._viewer)
        layout.setStretchFactor(self._viewer, 1)

    def task_output_changed(self):
        self._refresh_input_file()

    def _update_input_data(self):
        dynamic = self.get_dynamic_input_names()
        for name in self.get_input_names():
            self._default_inputs_form.set_parameter_enabled(name, name not in dynamic)

    def _refresh_input_file(self):
        filename = self.get_task_input_value("filename")
        if filename:
            self._viewer.updateFile(filename)

    def closeEvent(self, event):
        self._viewer.closeEvent(event)
