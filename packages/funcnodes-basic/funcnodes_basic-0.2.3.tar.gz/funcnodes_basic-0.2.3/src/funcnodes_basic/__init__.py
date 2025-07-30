from funcnodes_core import Shelf
from .logic import NODE_SHELF as logic_shelf
from .math_nodes import NODE_SHELF as math_shelf
from .lists import NODE_SHELF as lists_shelf
from .strings import NODE_SHELF as strings_shelf
from .dicts import NODE_SHELF as dicts_shelf
from .input import NODE_SHELF as input_shelf
from .dataclass import NODE_SHELF as dataclass_shelf

__version__ = "0.2.3"

NODE_SHELF = Shelf(
    nodes=[],
    subshelves=[
        input_shelf,
        lists_shelf,
        dicts_shelf,
        dataclass_shelf,
        strings_shelf,
        math_shelf,
        logic_shelf,
    ],
    name="basics",
    description="basic functionalities",
)
