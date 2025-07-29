from ewoksorange.bindings import OWEwoksWidgetNoThread
from ewoksorange.bindings import ow_build_opts
from ewoksorange.gui.parameterform import ParameterForm

from .data_viewer import DataViewer
from ..tasks.example_data.tasks import DEFAULTS
from . import serialize


class OWMeshWidget(OWEwoksWidgetNoThread, **ow_build_opts):
    def __init__(self):
        super().__init__()
        self._init_control_area()
        self._init_main_area()

    def _default_inputs_changed(self):
        self.update_default_inputs(**self._default_inputs_form.get_parameter_values())
        self._update_input_widgets()
        self._update_output_widgets()

    def handleNewSignals(self) -> None:
        self._update_input_widgets()
        super().handleNewSignals()

    def task_output_changed(self):
        self._update_output_widgets()

    def _init_control_area(
        self, stack: bool = False, multidetector: bool = False, mosaic: bool = False
    ):
        super()._init_control_area()
        self._default_inputs_form = ParameterForm(parent=self.controlArea)
        default = dict(DEFAULTS)
        if stack:
            default["nscans"] = 3
        else:
            default["nscans"] = 1
        if multidetector:
            default["ndetectors"] = 2
        else:
            default["ndetectors"] = 1
        values = self.get_default_input_values(include_missing=True, defaults=default)
        self.update_default_inputs(**values)

        parameters = {
            "output_filename": {
                "label": "HDF5 filename",
                "value_for_type": "",
                "select": "file",
            },
            "emission_line_groups": {
                "label": "Line groups",
                "value_for_type": "",
                "serialize": serialize.strings_serializer,
                "deserialize": serialize.strings_deserializer,
            },
            "rois": {
                "label": "Regions of interest",
                "value_for_type": "",
                "serialize": serialize.rois_serializer,
                "deserialize": serialize.rois_deserializer,
            },
            "energy": {
                "label": "Energy (keV)",
                "value_for_type": 0.0,
            },
            "shape": {
                "label": "Scan shape",
                "value_for_type": "",
                "serialize": serialize.shape_serializer,
                "deserialize": serialize.shape_deserializer,
            },
            "expo_time": {
                "label": "Exposure time (sec)",
                "value_for_type": 0.0,
            },
            "flux": {
                "label": "Flux (1/sec)",
                "value_for_type": 0.0,
            },
            "counting_noise": {
                "label": "Counting Noise",
                "value_for_type": False,
            },
            "integral_type": {
                "label": "Data as integers",
                "value_for_type": False,
            },
        }

        if mosaic:
            parameters["mosaic"] = {
                "label": "Mosaic chunks",
                "value_for_type": "",
                "serialize": serialize.shape_serializer,
                "deserialize": serialize.shape_deserializer,
            }

        if stack:
            parameters["nscans"] = {
                "label": "Number of scans",
                "value_for_type": 1,
            }

        if multidetector:
            parameters["ndetectors"] = {
                "label": "Number of detectors",
                "value_for_type": 0,
            }

        for name, kw in parameters.items():
            self._default_inputs_form.addParameter(
                name,
                value=values[name],
                value_change_callback=self._default_inputs_changed,
                **kw,
            )

    def _init_main_area(self):
        super()._init_main_area()
        layout = self._get_main_layout()

        self._viewer = DataViewer(parent=self.mainArea)
        self._viewer.setVisible(True)
        layout.addWidget(self._viewer)
        layout.setStretchFactor(self._viewer, 1)

        self._update_output_widgets()

    def _update_input_widgets(self):
        dynamic = self.get_dynamic_input_names()
        for name in self.get_input_names():
            self._default_inputs_form.set_parameter_enabled(name, name not in dynamic)

    def _update_output_widgets(self):
        self._refresh_output_file()

    def _refresh_output_file(self):
        filename = self.get_task_input_value("output_filename")
        if filename:
            self._viewer.updateFile(filename)
