"""
work with python dictionaries
"""

import funcnodes_core as fn
from typing import Any, List, Tuple


class DictGetNode(fn.Node):
    node_id = "dict_get"
    node_name = "Dict Get"
    dictionary = fn.NodeInput(id="dictionary", type=dict)
    key = fn.NodeInput(id="key", type=str)
    value = fn.NodeOutput(id="value", type=Any)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._keymap = {}
        self.get_input("dictionary").on("after_set_value", self._update_keys)

    def _update_keys(self, **kwargs):
        try:
            d = self.get_input("dictionary").value
            keys = list(d.keys())
        except KeyError:
            return
        keymap = dict({str(i): k for i, k in enumerate(keys)})
        reversed_keymap = {v: k for k, v in keymap.items()}
        self.get_input("key").update_value_options(options=reversed_keymap)
        self._keymap = keymap

    async def func(self, dictionary: dict, key: str) -> None:
        v = dictionary.get(self._keymap[key], fn.NoValue)
        self.outputs["value"].value = v
        return v


@fn.NodeDecorator(
    id="dict_keys",
    name="Dict Keys",
)
def dict_keys(dictionary: dict) -> List[Any]:
    return list(dictionary.keys())


@fn.NodeDecorator(
    id="dict_values",
    name="Dict Values",
)
def dict_values(dictionary: dict) -> List[Any]:
    return list(dictionary.values())


@fn.NodeDecorator(
    id="dict_items",
    name="Dict Items",
)
def dict_items(dictionary: dict) -> List[tuple]:
    return list(dictionary.items())


@fn.NodeDecorator(
    id="dict_from_items",
    name="Dict From Items",
)
def dict_from_items(items: List[tuple]) -> dict:
    return dict(items)


@fn.NodeDecorator(
    id="dict_from_keys_values",
    name="Dict From Keys Values",
)
def dict_from_keys_values(keys: List[Any], values: List[Any]) -> dict:
    return dict(zip(keys, values))


@fn.NodeDecorator(
    id="dict_to_lists",
    name="Dict to List",
    outputs=[
        {"name": "keys"},
        {
            "name": "values",
        },
    ],
)
def dict_to_list(dictionary: dict) -> Tuple[List[Any], List[Any]]:
    keys, values = zip(*dictionary.items())
    return list(keys), list(values)


NODE_SHELF = fn.Shelf(
    nodes=[
        DictGetNode,
        dict_keys,
        dict_values,
        dict_items,
        dict_from_items,
        dict_from_keys_values,
        dict_to_list,
    ],
    name="Dicts",
    description="Work with dictionaries",
    subshelves=[],
)
