from funcnodes_basic import dataclass as dc_nodes
import pytest_funcnodes
import pytest
import funcnodes_core as fn
from dataclasses import dataclass


@dataclass
class SimpleDataClass:
    name: str
    value: int
    is_active: bool = True


@dataclass
class NestedDataClass:
    id: int
    data: SimpleDataClass


@pytest_funcnodes.nodetest(dc_nodes.dataclass_to_dict)
async def test_dataclass_to_dict():
    node = dc_nodes.dataclass_to_dict()

    # Test with a simple dataclass
    instance1 = SimpleDataClass(name="Test1", value=100)
    node.inputs["instance"].value = instance1
    await node
    assert node.outputs["out"].value == {
        "name": "Test1",
        "value": 100,
        "is_active": True,
    }

    # Test with a nested dataclass
    instance2 = NestedDataClass(
        id=1, data=SimpleDataClass(name="Nested", value=200, is_active=False)
    )
    node.inputs["instance"].value = instance2
    await node
    assert node.outputs["out"].value == {
        "id": 1,
        "data": {"name": "Nested", "value": 200, "is_active": False},
    }

    # Test with non-dataclass input
    node.inputs["instance"].value = {"not": "a dataclass"}
    with pytest.raises(fn.NodeTriggerError) as excinfo:
        await node
    assert "Expected a dataclass instance" in str(excinfo.value)

    node.inputs["instance"].value = 123
    with pytest.raises(fn.NodeTriggerError) as excinfo:
        await node
    assert "Expected a dataclass instance" in str(excinfo.value)


@pytest_funcnodes.nodetest(dc_nodes.dataclass_get_field)
async def test_dataclass_get_field():
    node = dc_nodes.dataclass_get_field()

    instance_simple = SimpleDataClass(name="TestSimple", value=123)
    instance_nested = NestedDataClass(
        id=1, data=SimpleDataClass(name="Nested", value=200, is_active=False)
    )

    # Test setting instance updates field_name options
    node.inputs["instance"].value = instance_simple
    await node  # Initial trigger to process instance and update options
    assert node.inputs["field_name"].value_options["options"] == [
        "name",
        "value",
        "is_active",
    ]

    # Test getting a valid field 'name'
    node.inputs["field_name"].value = "name"
    await node
    assert node.outputs["out"].value == "TestSimple"

    # Test getting a valid field 'value'
    node.inputs["field_name"].value = "value"
    await node
    assert node.outputs["out"].value == 123

    # Test getting a valid field 'is_active'
    node.inputs["field_name"].value = "is_active"
    await node
    assert node.outputs["out"].value is True

    # Test with nested dataclass, first update options
    node.inputs["instance"].value = instance_nested

    assert node.inputs["field_name"].value_options["options"] == ["id", "data"]

    # Test getting 'id' from nested
    node.inputs["field_name"].value = "id"
    await node
    assert node.outputs["out"].value == 1

    # Test getting 'data' (which is another dataclass)
    node.inputs["field_name"].value = "data"
    await node
    assert node.outputs["out"].value == SimpleDataClass(
        name="Nested", value=200, is_active=False
    )

    # Test getting non-existent field
    node.inputs["instance"].value = instance_simple
    node.inputs["field_name"].value = "non_existent_field"
    with pytest.raises(fn.NodeTriggerError) as excinfo:
        await node
    assert "has no field 'non_existent_field'" in str(excinfo.value)

    # Test with non-dataclass input
    node.inputs["instance"].value = {"not": "a dataclass"}
    node.inputs["field_name"].value = "some_field"  # field_name options will be None
    assert node.inputs["field_name"].value_options["options"] is None

    with pytest.raises(fn.NodeTriggerError) as excinfo:
        await node  # trigger the func with invalid instance
    assert "Expected a dataclass instance" in str(excinfo.value)

    # Test dynamic update of options when instance changes
    node.inputs["instance"].value = instance_nested
    assert node.inputs["field_name"].value_options["options"] == ["id", "data"]
    node.inputs["field_name"].value = "id"
    await node
    assert node.outputs["out"].value == 1

    node.inputs["instance"].value = instance_simple
    assert node.inputs["field_name"].value_options["options"] == [
        "name",
        "value",
        "is_active",
    ]
    node.inputs[
        "field_name"
    ].value = "name"  # previous 'id' is no longer valid for options, but value remains
    await node
    assert node.outputs["out"].value == "TestSimple"
