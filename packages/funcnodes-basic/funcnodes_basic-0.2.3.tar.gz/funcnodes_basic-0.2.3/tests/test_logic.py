from funcnodes_basic import logic
from funcnodes_basic import math_nodes
import time
import funcnodes_core as fn
import pytest_funcnodes


@pytest_funcnodes.nodetest(logic.IfNode)
async def test_if_node():
    node = logic.IfNode()

    # Test when condition is True
    node.inputs["condition"].value = True
    node.inputs["input"].value = "true_value"
    await node
    assert node.outputs["on_true"].value == "true_value"
    assert node.outputs["on_false"].value == fn.NoValue

    # Test when condition is False
    node.inputs["condition"].value = False
    node.inputs["input"].value = "false_value"
    await node
    assert node.outputs["on_false"].value == "false_value"
    assert node.outputs["on_true"].value == "true_value"


@pytest_funcnodes.nodetest(logic.WaitNode)
async def test_wait_node():
    node = logic.WaitNode()

    # Test with a delay of 0.5 seconds
    node.inputs["delay"].value = 2
    node.inputs["input"].value = "waited_value"
    t = time.time()
    await node
    t_end = time.time() - t
    assert 2 <= t_end
    assert t_end < 4.5
    assert node.outputs["output"].value == "waited_value"


@pytest_funcnodes.nodetest(logic.ForNode)
async def test_for_node():
    node = logic.ForNode()
    node.inputs["input"].value = "hello"
    node.outputs["do"].connect(node.inputs["collector"])
    await node

    assert node.outputs["done"].value == ["h", "e", "l", "l", "o"]


@pytest_funcnodes.nodetest(logic.CollectorNode)
async def test_collector_node():
    node = logic.CollectorNode()

    # Test collecting values
    node.inputs["input"].value = "value1"
    await node
    assert node.outputs["output"].value == ["value1"]

    node.inputs["input"].value = "value2"
    await node
    assert node.outputs["output"].value == ["value1", "value2"]

    # Test resetting collection
    node.inputs["reset"].value = True
    node.inputs["input"].value = "value3"
    node.request_trigger()
    await node
    assert node.outputs["output"].value == ["value3"]

    # Test collecting again after reset
    node.inputs["input"].value = "value4"
    await node
    assert node.outputs["output"].value == ["value3", "value4"]


@pytest_funcnodes.nodetest(logic.WhileNode)
async def test_while_node():
    valuenode = math_nodes.value_node()
    valuenode.inputs["value"].value = 10
    await valuenode

    larger_than_5 = math_nodes.greater_node()
    larger_than_5.inputs["a"].connect(valuenode.outputs["out"])
    larger_than_5.inputs["b"].value = 5
    await larger_than_5
    assert larger_than_5.outputs["out"].value is True

    while_node = logic.WhileNode()
    while_node.inputs["condition"].connect(larger_than_5.outputs["out"])
    while_node.inputs["input"].connect(valuenode.outputs["out"])

    subtract_node = math_nodes.sub_node()
    subtract_node.inputs["a"].connect(while_node.outputs["do"])
    subtract_node.inputs["b"].value = 1
    subtract_node.outputs["out"].connect(valuenode.inputs["value"])

    await while_node

    subtract_node.outputs["out"].value <= 5
    subtract_node.outputs["out"].value >= 4
