from typing import Union
import funcnodes_core as fn


@fn.NodeDecorator(
    node_id="input.any",
    node_name="Input",
    description="Any input",
    outputs=[
        {"name": "out"},
    ],
)
def any_input(input: Union[str, float, int, bool]) -> str:
    return input


@fn.NodeDecorator(
    node_id="input.str",
    node_name="String Input",
    description="Input a string",
    outputs=[
        {"name": "string"},
    ],
)
def str_input(input: str) -> str:
    return str(input)


@fn.NodeDecorator(
    node_id="input.int",
    node_name="Integer Input",
    description="Input an integer",
    outputs=[
        {"name": "integer"},
    ],
)
def int_input(input: int) -> int:
    return int(input)


@fn.NodeDecorator(
    node_id="input.float",
    node_name="Float Input",
    description="Input a float",
    outputs=[
        {"name": "float"},
    ],
)
def float_input(input: float) -> float:
    return float(input)


@fn.NodeDecorator(
    node_id="input.bool",
    node_name="Boolean Input",
    description="Input a boolean",
    outputs=[
        {"name": "boolean"},
    ],
)
def bool_input(input: bool) -> bool:
    if isinstance(input, str):
        if input.lower() in ("true", "1", "yes"):
            input = True
        elif input.lower() in ("false", "0", "no"):
            input = False
    elif isinstance(input, (int, float)):
        input = bool(input)
    else:
        input = bool(input)
    return bool(input)


NODE_SHELF = fn.Shelf(
    nodes=[
        any_input,
        str_input,
        int_input,
        float_input,
        bool_input,
    ],
    name="Input",
    description="Simple input nodes",
)
