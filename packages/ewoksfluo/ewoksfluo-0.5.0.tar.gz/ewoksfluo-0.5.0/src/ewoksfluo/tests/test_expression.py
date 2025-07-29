from typing import Tuple, Any

import h5py

from ..math.expression import eval_expression
from ..math.expression import expression_variables
from ..tasks.math import eval_hdf5_expression


def test_eval_expression():
    expression = "np.mean([1,a,3,b])"
    variables = {"a": 2, "b": 4}
    eval_expression(expression, variables) == 2.5


def test_expression_variables():
    data = {"name A": 1, "name B": 2}

    def get_data(name: str) -> Tuple[str, Any]:
        return name, data[name]

    expression, variables, name_map = expression_variables(
        "<name A> * <name B>", get_data
    )
    assert expression == "data0 * data1"
    assert variables == {"data0": 1, "data1": 2}
    assert name_map == {"data0": "name A", "data1": "name B"}


def test_expression_variables_nondefault_brackets():
    data = {"name A": 1, "name B": 2}

    def get_data(name: str) -> Tuple[str, Any]:
        return name, data[name]

    expression, variables, name_map = expression_variables(
        "{name A} * {name B}", get_data, start_var="{", end_var="}"
    )
    assert expression == "data0 * data1"
    assert variables == {"data0": 1, "data1": 2}
    assert name_map == {"data0": "name A", "data1": "name B"}


def test_eval_hdf5_expression(tmp_path):
    filename = str(tmp_path / "data.h5")
    with h5py.File(filename, mode="w") as f:
        f["group/a"] = 2
        f["b"] = 4

    expression = "np.mean([1,<group/a>,3,<b>])"

    eval_hdf5_expression(filename, expression) == 2.5

    filename = str(tmp_path / "data.h5")
    with h5py.File(filename, mode="w") as f:
        f["root/group/a"] = 2
        f["root/b"] = 4

    expression = "np.mean([1,<group/a>,3,<b>])"

    eval_hdf5_expression(filename + "::/root", expression) == 2.5
