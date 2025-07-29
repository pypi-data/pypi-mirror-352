import json

from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.bindings import ow_build_opts
from ewoksorange.gui.parameterform import ParameterForm

from ewoksfluo.gui.data_viewer import DataViewer
from ewoksfluo.io.hdf5 import split_h5uri
from ewoksfluo.tasks.fit.tasks import DEFAULTS


class OWFitWidget(OWEwoksWidgetOneThread, **ow_build_opts):
    def __init__(self):
        super().__init__()
        self._multidetector = False
        self._init_control_area()
        self._init_main_area()

    def _init_control_area(self, stack: bool = False, multidetector: bool = False):
        self._multidetector = multidetector

        super()._init_control_area()
        self._default_inputs_form = ParameterForm(parent=self.controlArea)
        defaults = {
            **DEFAULTS,
            "output_root_uri": "processed_data.h5",
        }
        values = self.get_default_input_values(include_missing=True, defaults=defaults)
        self.update_default_inputs(**values)

        parameters = dict()

        if stack:
            parameters["bliss_scan_uris"] = {
                "label": "List of scan URIs",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
            }
        else:
            parameters["bliss_scan_uri"] = {
                "label": "Scan URI",
                "value_for_type": "",
                "select": "h5group",
            }
        parameters["output_root_uri"] = {
            "label": "Output URI",
            "value_for_type": "",
            "select": "h5group",
        }
        parameters["process_uri_template"] = {
            "label": "Process URI template",
            "value_for_type": "",
        }

        if multidetector:
            parameters["detector_names"] = {
                "label": "List of detector names",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
            }
        else:
            parameters["detector_name"] = {
                "label": "Detector name",
                "value_for_type": "",
            }
        parameters["xrf_spectra_uri_template"] = {
            "label": "XRF spectra URI template",
            "value_for_type": "",
        }

        if multidetector:
            parameters["configs"] = {
                "label": "List of PyMCA config URIs",
                "value_for_type": "",
                "serialize": json.dumps,
                "deserialize": json.loads,
            }
        else:
            parameters["config"] = {
                "label": "PyMCA config URI",
                "value_for_type": "",
                "select": "file",
            }

        parameters["energy_name"] = {
            "label": "Beam energy positioner name",
            "value_for_type": "",
        }
        parameters["energy_uri_template"] = {
            "label": "Beam energy positioner template",
            "value_for_type": "",
            "select": "h5group",
        }

        parameters["quantification"] = {
            "label": "Quantification",
            "value_for_type": False,
        }
        parameters["energy_multiplier"] = {
            "label": "Energy multiplier",
            "value_for_type": 0.0,
        }
        parameters["fast_fitting"] = {
            "label": "Fast",
            "value_for_type": False,
        }
        parameters["diagnostics"] = {
            "label": "Diagnostics",
            "value_for_type": False,
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
        self._update_input_widgets()
        self._update_output_widgets()

    def handleNewSignals(self) -> None:
        self._update_input_widgets()
        super().handleNewSignals()

    def task_output_changed(self):
        self._update_output_widgets()

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

    def _get_output_filenames(self):
        if self._multidetector:
            uris = self.get_task_output_value("xrf_results_uris")
            if not uris:
                return list()
            return [split_h5uri(uri)[0] for uri in uris]
        else:
            uri = self.get_task_output_value("xrf_results_uri")
            if not uri:
                return list()
            return [split_h5uri(uri)[0]]

    def _refresh_output_file(self):
        filenames = self._get_output_filenames()
        for filename in filenames:
            self._viewer.updateFile(filename)
