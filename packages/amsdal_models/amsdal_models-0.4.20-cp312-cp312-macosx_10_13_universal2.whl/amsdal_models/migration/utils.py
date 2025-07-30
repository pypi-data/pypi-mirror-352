import importlib
from pathlib import Path

from amsdal_utils.models.data_models.table_schema import NestedSchemaModel

reference_schema = NestedSchemaModel(
    properties={
        'ref': NestedSchemaModel(
            properties={
                'resource': str,
                'class_name': str,
                'class_version': str,
                'object_id': str,
                'object_version': str,
            },
        ),
    },
)


def contrib_to_module_root_path(contrib: str) -> Path:
    """
    Converts a contrib string to the root path of the module.

    Args:
        contrib (str): The contrib string to convert.

    Returns:
        Path: The root path of the module.
    """
    contrib_root = '.'.join(contrib.split('.')[:-2])
    contrib_root_module = importlib.import_module(contrib_root)

    return Path(contrib_root_module.__path__[0])
