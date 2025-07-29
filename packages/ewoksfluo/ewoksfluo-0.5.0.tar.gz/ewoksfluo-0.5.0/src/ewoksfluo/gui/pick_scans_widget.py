from typing import Callable, Mapping, Optional
from AnyQt import QtWidgets
from ewoksorange.gui.parameterform import ParameterForm
from ewokscore import missing_data

from . import serialize


class PickScansWidget(QtWidgets.QWidget):
    def __init__(
        self,
        default_inputs_change_callback: Callable,
        initial_values: Optional[Mapping] = None,
    ):
        super().__init__()

        if initial_values is None:
            initial_values = {}

        self.form = ParameterForm(parent=self)
        self._default_inputs_change_callback = default_inputs_change_callback

        parameters = {
            "filename": {
                "label": "HDF5 filename",
                "value_for_type": "",
                "select": "file",
            },
            "scan_min": {
                "label": "Minimum scan to include",
                "value_for_type": 1,
            },
            "scan_max": {
                "label": "Maximum scan to include",
                "value_for_type": 1,
            },
            "exclude_scans": {
                "label": "List of scans to exclude",
                "value_for_type": "",
                "serialize": serialize.integers_serializer,
                "deserialize": serialize.integers_deserializer,
            },
        }

        for name, kw in parameters.items():
            self.form.addParameter(
                name,
                value=initial_values.get(name, missing_data.MISSING_DATA),
                value_change_callback=self._default_inputs_changed,
                **kw,
            )

    def _default_inputs_changed(self) -> None:
        self._default_inputs_change_callback(self.form.get_parameter_values())
