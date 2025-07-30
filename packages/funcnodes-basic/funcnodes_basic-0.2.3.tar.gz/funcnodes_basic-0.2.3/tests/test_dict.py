from funcnodes_basic import dicts
import pytest_funcnodes
# DictGetNode,
# dict_keys,
# dict_values,
# dict_items,
# dict_from_items,
# dict_from_keys_values,
# dict_to_list,


@pytest_funcnodes.nodetest(dicts.DictGetNode)
async def test_dict_get():
    testdict = {"a": 1, "b": 2, "c": 3}

    node = dicts.DictGetNode()

    node.inputs["dictionary"].value = testdict
    await node

    assert node.inputs["key"].value_options["options"] == {"a": "0", "b": "1", "c": "2"}

    node.inputs["key"].value = "0"
    await node

    assert node.outputs["value"].value == 1


@pytest_funcnodes.nodetest(dicts.dict_keys)
async def test_dict_keys():
    testdict = {"a": 1, "b": 2, "c": 3}

    node = dicts.dict_keys()

    node.inputs["dictionary"].value = testdict
    await node

    assert node.outputs["out"].value == ["a", "b", "c"]


@pytest_funcnodes.nodetest(dicts.dict_values)
async def test_dict_values():
    testdict = {"a": 1, "b": 2, "c": 3}

    node = dicts.dict_values()

    node.inputs["dictionary"].value = testdict
    await node

    assert node.outputs["out"].value == [1, 2, 3]


@pytest_funcnodes.nodetest(dicts.dict_items)
async def test_dict_items():
    testdict = {"a": 1, "b": 2, "c": 3}

    node = dicts.dict_items()

    node.inputs["dictionary"].value = testdict
    await node

    assert node.outputs["out"].value == [("a", 1), ("b", 2), ("c", 3)]


@pytest_funcnodes.nodetest(dicts.dict_from_items)
async def test_dict_from_items():
    testitems = [("a", 1), ("b", 2), ("c", 3)]

    node = dicts.dict_from_items()

    node.inputs["items"].value = testitems
    await node

    assert node.outputs["out"].value == {"a": 1, "b": 2, "c": 3}


@pytest_funcnodes.nodetest(dicts.dict_from_keys_values)
async def test_dict_from_keys_values():
    testkeys = ["a", "b", "c"]
    testvalues = [1, 2, 3]

    node = dicts.dict_from_keys_values()

    node.inputs["keys"].value = testkeys
    node.inputs["values"].value = testvalues
    await node

    assert node.outputs["out"].value == {"a": 1, "b": 2, "c": 3}


@pytest_funcnodes.nodetest(dicts.dict_to_list)
async def test_dict_to_list():
    testdict = {"a": 1, "b": 2, "c": 3}

    node = dicts.dict_to_list()

    node.inputs["dictionary"].value = testdict
    await node

    assert node.outputs["keys"].value == ["a", "b", "c"]
    assert node.outputs["values"].value == [1, 2, 3]
