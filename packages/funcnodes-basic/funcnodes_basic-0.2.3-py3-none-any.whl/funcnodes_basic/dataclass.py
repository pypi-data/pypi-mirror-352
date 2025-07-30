import dataclasses
import funcnodes_core as fn
from typing import Any, Dict


@fn.NodeDecorator(
    id="dataclass.to_dict",
)
def dataclass_to_dict(instance: Any) -> Dict[str, Any]:
    """
    Convert a dataclass instance to a dictionary.

    Args:
        instance (object): The dataclass instance to convert.

    Returns:
        dict: The dictionary representation of the dataclass instance.
    """
    if not dataclasses.is_dataclass(instance):
        raise TypeError(f"Expected a dataclass instance, got {type(instance)}")

    return dataclasses.asdict(instance)


@fn.NodeDecorator(
    id="dataclass.get_field",
    default_io_options={
        "instance": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_value_options(
                    "field_name",
                    lambda result: {
                        "options": [field.name for field in dataclasses.fields(result)]
                        if dataclasses.is_dataclass(result)
                        else None,
                    },
                )
            }
        }
    },
)
def dataclass_get_field(instance: Any, field_name: str) -> Any:
    """
    Get a field value from a dataclass instance.
    """
    if not dataclasses.is_dataclass(instance):
        raise TypeError(f"Expected a dataclass instance, got {type(instance)}")

    if not hasattr(instance, field_name):
        raise AttributeError(
            f"{instance.__class__.__name__} has no field '{field_name}'"
        )

    return getattr(instance, field_name)


NODE_SHELF = fn.Shelf(
    nodes=[
        dataclass_to_dict,
        dataclass_get_field,
    ],
    name="dataclass",
    description="Nodes for working with dataclasses",
)
