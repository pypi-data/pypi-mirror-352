import inspect
from typing import Callable, List


def get_fct_parameter_names(fct: Callable) -> List[str]:
    """
    Returns the list of parameter names from the given function.

    Args:
        fct (Callable): The function to extract parameters from.

    Returns:
        List[str]: The list of parameter names.
    """
    return list(inspect.signature(fct).parameters.keys())
