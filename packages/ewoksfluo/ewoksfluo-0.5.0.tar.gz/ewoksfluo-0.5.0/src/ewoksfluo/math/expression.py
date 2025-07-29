import re
from typing import Dict, Any, Tuple, Callable

import numpy

from . import pad


def expression_variables(
    expression: str,
    get_data: Callable[[str], Tuple[str, Any]],
    start_var: str = "<",
    end_var: str = ">",
) -> Tuple[str, Dict[str, Any], Dict[str, str]]:
    """Return the variables and associated expression to be evaluated.

    :param expression: for example `"<name A> * <name B>"`
    :param get_data: takes a variable name as input and returns its full name and value
    :param start_var: marks the start of a variable name
    :param end_var: marks the end of a variable name
    :returns: expression, variables and name map. For example expression `"data0 * data1"`,
              variables `{"data0":..., "data1":...}` and name map `{"data0":"name A", "data1":"name B"}`.
    """
    pattern = rf"{re.escape(start_var)}([^{re.escape(end_var)}]+){re.escape(end_var)}"

    variables = {}
    name_map = {}
    for i, variable_name in enumerate(re.findall(pattern, expression)):
        new_name = f"data{i}"
        name_map[new_name], variables[new_name] = get_data(variable_name)
        expression = expression.replace(
            f"{start_var}{variable_name}{end_var}", new_name
        )

    max_len = pad.pad_length(variables)
    if max_len is not None:
        pad.pad_arrays(max_len, variables)

    return expression, variables, name_map


def eval_expression(expression: str, variables: Dict[str, Any]) -> Any:
    """Evaluate an arithmetic expression with python and numpy arithmetic.

    :param expression: arithmetic expression where datasets are define as
                       `data1` where `data1`
                       must be a key in `variables`.
    :param variables: variables to be used in the expression
    """
    globals = {"__builtins__": {"len": len, "sum": sum}, "np": numpy, "numpy": numpy}
    return eval(expression, globals, variables)
