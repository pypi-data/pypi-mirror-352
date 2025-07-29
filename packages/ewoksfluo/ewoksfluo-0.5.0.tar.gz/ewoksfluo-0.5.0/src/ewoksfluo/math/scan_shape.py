import re
from typing import Dict, List, Optional, Callable
from scipy.optimize import least_squares


def solve_scan_shape(
    num_scan_points: List[int], equations: List[str]
) -> Optional[Dict[str, int]]:
    """Compute the scan shape based on a number of scan points and their parametrization.

    :params num_scan_points: A list of scan points.
    :param equations: A parametrization of the list of scan points.
    :returns: If the solver, a dictionary containing the solved integer values for each variable.
    """
    if len(equations) != len(num_scan_points):
        raise ValueError("Number of equations and number scan points must be the same")
    keys = [f"npoints{i}" for i in range(len(equations))]
    equations_dict = dict(zip(keys, equations))
    values_dict = dict(zip(keys, num_scan_points))

    def estimate_initial_values(nunknowns) -> List[int]:
        min_value = min(values_dict.values())
        return [max(1.0, min_value ** (1 / nunknowns))] * nunknowns

    return solve_nnls_posint(equations_dict, values_dict, estimate_initial_values)


def solve_nnls_posint(
    equations_dict: Dict[str, str],
    values_dict: Dict[str, int],
    estimate_initial_values: Optional[Callable[[int], List[int]]] = None,
) -> Optional[Dict[str, int]]:
    """Solve a system of non-linear equations with strictly positive integer constraints, supporting over-determined systems.

    :param equations_dict: A dictionary where keys are equation names and values are the equations as strings.
    :param values_dict: A dictionary where keys match those in equations_dict and values are the known results.
    :returns: If the solver, a dictionary containing the solved integer values for each variable.
    :raises ValueError: If the keys in equations_dict and values_dict do not match.
    """
    if set(equations_dict.keys()) != set(values_dict.keys()):
        raise ValueError("Mismatch between equations and values dictionary keys")
    if not equations_dict:
        return

    unknowns = set()
    for eq in equations_dict.values():
        unknowns.update(re.findall(r"[a-zA-Z_]\w*", eq))
    unknowns -= set(values_dict.keys())  # Remove constants
    unknowns = sorted(unknowns)

    def residuals(vars: List[float]) -> List[float]:
        local_vars = dict(zip(unknowns, vars))
        residuals = []
        for key, equation in equations_dict.items():
            # Evaluate each equation with current variable values
            residual = (
                eval(equation, {}, {**local_vars, **values_dict}) - values_dict[key]
            )
            residuals.append(residual)
        return residuals

    nunknowns = len(unknowns)
    if estimate_initial_values:
        initial_guess = estimate_initial_values(nunknowns)
    else:
        initial_guess = [1.0] * nunknowns

    bounds = (1, [float("inf")] * nunknowns)
    result = least_squares(residuals, initial_guess, bounds=bounds)
    final_values = list(map(round, result.x))

    final_residuals = residuals(final_values)
    if any(final_residuals):
        return

    return dict(zip(unknowns, final_values))
