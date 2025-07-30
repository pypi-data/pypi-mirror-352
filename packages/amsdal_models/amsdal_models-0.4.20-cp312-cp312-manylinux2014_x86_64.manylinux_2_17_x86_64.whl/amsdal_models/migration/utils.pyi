from _typeshed import Incomplete
from pathlib import Path

reference_schema: Incomplete

def contrib_to_module_root_path(contrib: str) -> Path:
    """
    Converts a contrib string to the root path of the module.

    Args:
        contrib (str): The contrib string to convert.

    Returns:
        Path: The root path of the module.
    """
