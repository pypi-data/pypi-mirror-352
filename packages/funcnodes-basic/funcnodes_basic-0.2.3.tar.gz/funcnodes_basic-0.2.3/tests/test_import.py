import funcnodes as fn


def test_find():
    res = fn.lib.libfinder.find_shelf_from_module("funcnodes_basic")

    assert res[0].name == "basics", res
    len(res[0].subshelves) > 0
