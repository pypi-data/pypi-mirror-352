import re
from typing import Any, Tuple

from ..io.hdf5 import split_h5uri
from ..io.hdf5 import ReadHdf5File
from ..math.expression import eval_expression
from ..math.expression import expression_variables


def format_expression_template(template: str, name: str) -> str:
    n = len(re.findall(r"\{\}", template))
    return template.format(*[name] * n)


def eval_hdf5_expression(
    data_uri: str, expression: str, start_var: str = "<", end_var: str = ">"
) -> Any:
    """Evaluate an arithmetic expression with python and numpy arithmetic
    on HDF5 datasets.

    :param data_uri: HDF5 root URI
    :param expression: arithmetic expression where datasets are define as
                       :code:`"<subgroup/data>"` where :code:`"subgroup/data"`
                       is relative to :code:`data_uri`.
    :param start_var: marks the start of a variable name
    :param end_var: marks the end of a variable name
    """
    data_file, data_h5path = split_h5uri(data_uri)

    with ReadHdf5File(data_file) as h5file:
        if not data_h5path:
            data_h5path = "/"
        data_root = h5file[data_h5path]

        def get_data(path: str) -> Tuple[str, Any]:
            return path, data_root[path][()]

        expression, variables, _ = expression_variables(
            expression, get_data, start_var=start_var, end_var=end_var
        )

    return eval_expression(expression, variables)
