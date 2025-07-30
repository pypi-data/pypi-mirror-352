from pytest_funcnodes import all_nodes_tested
import funcnodes_basic as fnmodule  # noqa


def test_all_nodes_tested(all_nodes):
    all_nodes_tested(all_nodes, fnmodule.NODE_SHELF, ignore=[])
