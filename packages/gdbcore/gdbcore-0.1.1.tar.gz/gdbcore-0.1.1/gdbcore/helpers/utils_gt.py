import sys

import pandas as pd

# found by running brew --prefix graph-tool
sys.path.append("/opt/homebrew/opt/graph-tool/lib/python3.12/site-packages/")
sys.path.append("../kgqc/")
import os
import re

import graph_tool.all as gt

from gdbcore.helpers.utils import assert_path, filter_filepaths

# function to get graphml load formatted properly


def rename_vertex_property(g, mapping):
    """
    mapping is a dictionary with the original name as a key and the rename as value
    similar to pd.DataFrame.rename() method
    """

    # PRECONDITIONS
    assert isinstance(mapping, dict), f"mapping must be a dictionary {mapping}"
    for k in mapping:
        assert (
            k in g.vp.keys()
        ), f"{k} does not exist as a vertex property: {list(g.vp.keys())}"

    # MAIN FUNCTION
    for prop_name in mapping:
        # get the rename
        new_name = mapping[prop_name]
        # verbose
        print(f"Renaming {prop_name} to {new_name}...")

        # get the original vertex property's datatype
        val_type = g.vp[prop_name].value_type()

        # init the new vertex property
        g.vp[new_name] = g.new_vertex_property(val_type)
        # check was the vp created
        assert (
            new_name in g.vp.keys()
        ), f"{new_name} was not created as a vertex property {list(g.vp.keys())}"

        # copy over the data
        g.copy_property(g.vp[prop_name], g.vp[new_name])

        # MORE POST CONDITIONAL CHECKS
        # are the values the same in both
        assert all(
            [x == y for x, y in zip(g.vp[prop_name], g.vp[new_name])]
        ), f"issue copying {prop_name} to {new_name}"

        # verbose
        print(f"{prop_name} renamed to {new_name}. Deleting {prop_name}...")
        # rm the old one
        del g.vp[prop_name]

        # MORE POSTCONDITIONS
        assert (
            prop_name not in g.vp.keys()
        ), f"not able to delete {prop_name} from {list(g.vp.keys())}"

    return g.vp


def rename_edge_property(g, mapping):
    """
    mapping is a dictionary with the original name as a key and the rename as value
    """

    # PRECONDITIONS
    assert isinstance(mapping, dict), f"mapping must be a dictionary {mapping}"
    for k in mapping:
        assert (
            k in g.ep.keys()
        ), f"{k} does not exist as a vertex property: {list(g.ep.keys())}"

    # MAIN FUNCTION
    for prop_name in mapping:
        # get the rename
        new_name = mapping[prop_name]
        # verbose
        print(f"Renaming {prop_name} to {new_name}...")

        # get the original vertex property's datatype
        val_type = g.ep[prop_name].value_type()

        # init the new vertex property
        g.ep[new_name] = g.new_edge_property(val_type)

        # copy over the data
        g.copy_property(g.ep[prop_name], g.ep[new_name])

        # SOME POSTCONDITIONAL CHECKS
        # was the vp created
        assert (
            new_name in g.ep.keys()
        ), f"{new_name} was not created as a vertex property {list(g.ep.keys())}"
        # are the values the same in both
        assert all(
            [x == y for x, y in zip(g.ep[prop_name], g.ep[new_name])]
        ), f"issue copying {prop_name} to {new_name}"

        # verbose
        print(f"{prop_name} renamed to {new_name}. Deleting {prop_name}...")
        # rm the old one
        del g.ep[prop_name]

        # MORE POSTCONDITIONS
        assert (
            prop_name not in g.ep.keys()
        ), f"not able to delete {prop_name} from {list(g.ep.keys())}"
    return g.ep
