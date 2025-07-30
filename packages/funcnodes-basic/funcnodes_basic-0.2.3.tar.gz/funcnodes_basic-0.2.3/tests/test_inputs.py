from funcnodes_basic import input
import pytest_funcnodes
import pytest
import funcnodes_core as fn


@pytest_funcnodes.nodetest(input.any_input)
async def test_any_input():
    node = input.any_input()

    node.inputs["input"].value = 1
    await node

    assert node.outputs["out"].value == 1

    node.inputs["input"].value = "test"
    await node

    assert node.outputs["out"].value == "test"

    node.inputs["input"].value = [1, 2, 3]
    await node

    assert node.outputs["out"].value == [1, 2, 3]


@pytest_funcnodes.nodetest(input.str_input)
async def test_str_input():
    node = input.str_input()

    node.inputs["input"].value = 1
    await node

    assert node.outputs["string"].value == "1"

    node.inputs["input"].value = "test"
    await node

    assert node.outputs["string"].value == "test"

    node.inputs["input"].value = [1, 2, 3]
    await node

    assert node.outputs["string"].value == "[1, 2, 3]"


@pytest_funcnodes.nodetest(input.int_input)
async def test_int_input():
    node = input.int_input()

    node.inputs["input"].value = 1
    await node
    node.inputs["input"].value = "test"

    with pytest.raises(fn.NodeTriggerError):
        await node

    node.inputs["input"].value = [1, 2, 3]

    with pytest.raises(fn.NodeTriggerError):
        await node

    node.inputs["input"].value = 1.5
    await node
    assert node.outputs["integer"].value == 1


@pytest_funcnodes.nodetest(input.float_input)
async def test_float_input():
    node = input.float_input()

    node.inputs["input"].value = 1
    await node

    assert node.outputs["float"].value == 1.0

    node.inputs["input"].value = "test"

    with pytest.raises(fn.NodeTriggerError):
        await node

    node.inputs["input"].value = [1, 2, 3]

    with pytest.raises(fn.NodeTriggerError):
        await node

    node.inputs["input"].value = "1.5"
    await node
    assert node.outputs["float"].value == 1.5


@pytest_funcnodes.nodetest(input.bool_input)
async def test_bool_input():
    node = input.bool_input()

    node.inputs["input"].value = 1
    await node

    assert node.outputs["boolean"].value is True

    node.inputs["input"].value = "test"
    await node
    assert node.outputs["boolean"].value is True

    node.inputs["input"].value = ""
    await node
    assert node.outputs["boolean"].value is False

    node.inputs["input"].value = [1, 2, 3]
    await node
    assert node.outputs["boolean"].value is True

    node.inputs["input"].value = None
    await node
    assert node.outputs["boolean"].value is False

    node.inputs["input"].value = "True"
    await node
    assert node.outputs["boolean"].value is True

    node.inputs["input"].value = "False"
    await node
    assert node.outputs["boolean"].value is False
