from typing import List, Union, Any, Tuple
import funcnodes_core as fn
import copy


@fn.NodeDecorator(
    id="contains_node",
    name="Contains",
)
def contains(collection: List[Union[str, Any]], item: Union[str, Any]) -> bool:
    return item in collection


@fn.NodeDecorator(
    id="list_get",
    name="Get Element",
    description="Gets an element from a list.",
    default_io_options={
        "lst": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_value_options(
                    "index",
                    lambda result: {
                        "min": -len(result),
                        "max": len(result) - 1 if len(result) > 0 else 0,
                    },
                )
            }
        },
    },
    outputs=[
        {"name": "element"},
    ],
)
def list_get(lst: List[Any], index: int = -1) -> Tuple[Any]:
    # shallow copy the list
    return lst[index]


@fn.NodeDecorator(
    id="to_list",
    name="To List",
)
def to_list(obj: Any) -> List[Any]:
    try:
        return list(obj)
    except TypeError:
        return [obj]


@fn.NodeDecorator(
    id="list_length",
    name="List Length",
)
def list_length(lst: List[Any]) -> int:
    return len(lst)


@fn.NodeDecorator(
    id="list_append",
    name="List Append",
)
def list_append(lst: List[Any], item: Any) -> List[Any]:
    return lst + [item]


@fn.NodeDecorator(
    id="list_extend",
    name="List Extend",
)
def list_extend(lst: List[Any], items: List[Any]) -> List[Any]:
    return lst + items


@fn.NodeDecorator(
    id="list_pop",
    name="List Pop",
    default_io_options={
        "lst": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_value_options(
                    "index",
                    lambda result: {
                        "min": -len(result),
                        "max": len(result) - 1 if len(result) > 0 else 0,
                    },
                )
            }
        },
    },
    outputs=[
        {"name": "new_list"},
        {"name": "item"},
    ],
)
def list_pop(lst: List[Any], index: int = -1) -> Tuple[List[Any], Any]:
    # shallow copy the list
    lst = copy.copy(lst)
    item = lst.pop(index)
    return lst, item


@fn.NodeDecorator(
    id="list_remove",
    name="List Remove",
)
def list_remove(lst: List[Any], item: Any, all: bool = False) -> List[Any]:
    lst = copy.copy(lst)
    if item in lst:
        lst.remove(item)
    if all:
        while item in lst:
            lst.remove(item)
    return lst


@fn.NodeDecorator(
    id="list_index",
    name="List Index",
)
def list_index(lst: List[Any], item: Any) -> int:
    return lst.index(item)


@fn.NodeDecorator(
    id="list_reverse",
    name="List Reverse",
)
def list_reverse(lst: List[Any]) -> List[Any]:
    lst = copy.copy(lst)
    lst.reverse()
    return lst


@fn.NodeDecorator(
    id="list_sort",
    name="List Sort",
)
def list_sort(lst: List[Any], reverse: bool = False) -> List[Any]:
    lst = copy.copy(lst)
    lst.sort(reverse=reverse)
    return lst


@fn.NodeDecorator(
    id="list_count",
    name="List Count",
)
def list_count(lst: List[Any], item: Any) -> int:
    return lst.count(item)


@fn.NodeDecorator(
    id="list_insert",
    name="List Insert",
    default_io_options={
        "lst": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_value_options(
                    "index",
                    lambda result: {
                        "min": -len(result),
                        "max": len(result),
                    },
                )
            }
        },
    },
)
def list_insert(lst: List[Any], item: Any, index: int = -1) -> List[Any]:
    lst = copy.copy(lst)
    lst.insert(index, item)
    return lst


@fn.NodeDecorator(
    id="list_set",
    name="List Set",
    default_io_options={
        "lst": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_value_options(
                    "index",
                    lambda result: {
                        "min": -len(result),
                        "max": len(result) - 1 if len(result) > 0 else 0,
                    },
                )
            }
        },
    },
)
def list_set(lst: List[Any], item: Any, index: int = -1) -> List[Any]:
    lst = copy.copy(lst)
    lst[index] = item
    return lst


@fn.NodeDecorator(
    id="list_slice",
    name="List Slice",
    default_io_options={
        "lst": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_value_options(
                    ["start", "end"],
                    lambda result: {"min": -len(result), "max": len(result) + 1},
                ),
            }
        },
    },
)
def list_slice(lst: List[Any], start: int = 0, end: int = -1) -> List[Any]:
    return lst[start:end]


@fn.NodeDecorator(
    id="list_slice_step",
    name="List Slice Step",
    default_io_options={
        "lst": {
            "on": {
                "after_set_value": fn.decorator.update_other_io_value_options(
                    ["start", "end"],
                    lambda result: {"min": -len(result), "max": len(result) + 1},
                ),
            }
        },
    },
)
def list_slice_step(
    lst: List[Any], start: int = 0, end: int = -1, step: int = 1
) -> List[Any]:
    return lst[start:end:step]


NODE_SHELF = fn.Shelf(
    nodes=[
        contains,
        list_get,
        to_list,
        list_length,
        list_append,
        list_extend,
        list_pop,
        list_remove,
        list_index,
        list_reverse,
        list_sort,
        list_count,
        list_insert,
        list_set,
        list_slice,
        list_slice_step,
    ],
    subshelves=[],
    name="Lists",
    description="List operations",
)
