from funcnodes_basic import lists
import pytest_funcnodes
import funcnodes as fn

fn.config.set_in_test()


@pytest_funcnodes.nodetest(lists.list_get)
async def test_list_getindex():
    testlist = [1, 2, 3]

    node = lists.list_get()

    node.inputs["lst"].value = testlist
    await node

    assert node.outputs["element"].value == 3

    node.inputs["index"].value = 1
    await node

    assert node.outputs["element"].value == 2


@pytest_funcnodes.nodetest(lists.contains)
async def test_list_contains():
    testlist = [1, 2, 3]

    node = lists.contains()

    node.inputs["collection"].value = testlist
    node.inputs["item"].value = 2
    await node

    assert node.outputs["out"].value is True


@pytest_funcnodes.nodetest(lists.to_list)
async def test_to_list():
    node = lists.to_list()

    node.inputs["obj"].value = 1
    await node

    assert node.outputs["out"].value == [1]


@pytest_funcnodes.nodetest(lists.list_length)
async def test_list_length():
    testlist = [1, 2, 3]

    node = lists.list_length()

    node.inputs["lst"].value = testlist
    await node

    assert node.outputs["out"].value == 3


@pytest_funcnodes.nodetest(lists.list_append)
async def test_list_append():
    testlist = [1, 2, 3]

    node = lists.list_append()

    node.inputs["lst"].value = testlist
    node.inputs["item"].value = 4
    await node

    assert node.outputs["out"].value == [1, 2, 3, 4]
    assert testlist == [1, 2, 3]


@pytest_funcnodes.nodetest(lists.list_extend)
async def test_list_extend():
    testlist = [1, 2, 3]

    node = lists.list_extend()

    node.inputs["lst"].value = testlist
    node.inputs["items"].value = [4, 5]
    await node

    assert node.outputs["out"].value == [1, 2, 3, 4, 5]
    assert testlist == [1, 2, 3]


@pytest_funcnodes.nodetest(lists.list_pop)
async def test_list_pop():
    testlist = [1, 2, 3]

    node = lists.list_pop()

    node.inputs["lst"].value = testlist
    node.inputs["index"].value = 1
    await node

    assert node.outputs["new_list"].value == [1, 3]
    assert testlist == [1, 2, 3]

    assert node.outputs["item"].value == 2


@pytest_funcnodes.nodetest(lists.list_remove)
async def test_list_remove():
    testlist = [1, 2, 3, 3, 3]

    node = lists.list_remove()

    node.inputs["lst"].value = testlist
    node.inputs["item"].value = 3
    await node

    assert node.outputs["out"].value == [1, 2, 3, 3]
    assert testlist == [1, 2, 3, 3, 3]
    node.inputs["all"].value = True
    await node

    assert node.outputs["out"].value == [1, 2]
    assert testlist == [1, 2, 3, 3, 3]


@pytest_funcnodes.nodetest(lists.list_index)
async def test_list_index():
    testlist = [1, 2, 3]

    node = lists.list_index()

    node.inputs["lst"].value = testlist
    node.inputs["item"].value = 2
    await node

    assert node.outputs["out"].value == 1


@pytest_funcnodes.nodetest(lists.list_reverse)
async def test_list_reverse():
    testlist = [1, 2, 3]

    node = lists.list_reverse()

    node.inputs["lst"].value = testlist
    await node

    assert node.outputs["out"].value == [3, 2, 1]
    assert testlist == [1, 2, 3]


@pytest_funcnodes.nodetest(lists.list_sort)
async def test_list_sort():
    testlist = [3, 2, 1]

    node = lists.list_sort()

    node.inputs["lst"].value = testlist
    await node

    assert node.outputs["out"].value == [1, 2, 3]
    assert testlist == [3, 2, 1]

    node.inputs["reverse"].value = True
    await node

    assert node.outputs["out"].value == [3, 2, 1]
    assert testlist == [3, 2, 1]


@pytest_funcnodes.nodetest(lists.list_count)
async def test_list_count():
    testlist = [1, 2, 3, 3]

    node = lists.list_count()

    node.inputs["lst"].value = testlist
    node.inputs["item"].value = 3
    await node

    assert node.outputs["out"].value == 2


@pytest_funcnodes.nodetest(lists.list_insert)
async def test_list_insert():
    testlist = [1, 2, 3]

    node = lists.list_insert()

    node.inputs["lst"].value = testlist
    node.inputs["index"].value = 1
    node.inputs["item"].value = 4
    await node

    assert node.outputs["out"].value == [1, 4, 2, 3]
    assert testlist == [1, 2, 3]


@pytest_funcnodes.nodetest(lists.list_set)
async def test_list_set():
    testlist = [1, 2, 3]

    node = lists.list_set()

    node.inputs["lst"].value = testlist
    node.inputs["index"].value = 1
    node.inputs["item"].value = 4
    await node

    assert node.outputs["out"].value == [1, 4, 3]
    assert testlist == [1, 2, 3]


@pytest_funcnodes.nodetest(lists.list_slice)
async def test_list_slice():
    testlist = [1, 2, 3, 4]

    node = lists.list_slice()

    node.inputs["lst"].value = testlist
    node.inputs["start"].value = 1
    node.inputs["end"].value = 3
    await node

    assert node.outputs["out"].value == [2, 3]
    assert testlist == [1, 2, 3, 4]


@pytest_funcnodes.nodetest(lists.list_slice_step)
async def test_list_slice_step():
    testlist = [1, 2, 3, 4, 5]

    node = lists.list_slice_step()

    node.inputs["lst"].value = testlist
    node.inputs["start"].value = 1
    node.inputs["end"].value = 4
    node.inputs["step"].value = 2
    await node

    assert node.outputs["out"].value == [2, 4]
    assert testlist == [1, 2, 3, 4, 5]
