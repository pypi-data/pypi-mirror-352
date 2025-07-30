"""
The purpose of this script is to take rando csvs (but can also combine with actual node and edge lists) and create initial node and edge lists as csvs

Any additional cleaning of the node and edge lists can be done any way you prefer outside of this script. 

Requirements:
- headers should be attached to the csv files

TODO 
- add explanation of config file
- add more log statements
- update overall readme of this whole repo 
- prepare 
"""

# imports
import os
import re

import numpy as np
import pandas as pd

# import modules
from gdbcore.helpers.utils import (
    assert_nonempty_keys,
    assert_nonempty_vals,
    config_loader,
    copy_recursively,
    filter_filepaths,
    get_args,
    get_logger,
)
from gdbcore.helpers.utils_cypher import cypher_camelcase, cypher_upper


def main(config_path:str):

    ## PRECONDITIONS
    if not isinstance(config_path, str):
        raise TypeError("config_path must be a string")
    # check if config_path exists
    if not os.path.isfile(os.path.abspath(config_path)):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    ## MAIN FUNCTION
    # START LOG FILE
    logger = get_logger()
    logger.info(f"Using config: {config_path}")

    # LOAD CONFIG PARAMETERS
    logger.info("Loading config params ... ")
    config = config_loader(config_path)["list_builder"]
    assert_nonempty_keys(config)
    assert_nonempty_vals(config)
    logger.info(f"Configuration: {config}")

    # incoming file conditions
    src_sep = config["source"]["sep"]
    src_quotechar = config["source"]["quotechar"]

    # outcoming file settings
    out_fpath = config["output"]["folder path"]
    out_prefix = config["output"]["prefix"]
    out_sep_header = config["output"]["separate header"]
    out_sep = config["output"]["sep"]
    out_quotechar = config["output"]["quotechar"]
    # column names corresponding to
    assert_nonempty_keys(config["output"]["col_names"])
    assert_nonempty_vals(config["output"]["col_names"])
    out_node_ids = config["output"]["col_names"]["node_ids"]
    out_node_labels = config["output"]["col_names"]["node_labels"]
    out_edge_labels = config["output"]["col_names"]["edge_labels"]
    out_start_ids = config["output"]["col_names"]["start_ids"]
    out_end_ids = config["output"]["col_names"]["end_ids"]
    out_cypher = config["output"]["cypher_formatting"]

    # starting with making the node lists
    for node in config["nodes"]:

        logger.info(f"Creating {node} list...")

        node_naming = re.sub(r"[^A-Za-z]+$", "", node)

        node_config = config["nodes"][node]
        id_file = config["source files"][node_config["id"][0]]
        id_config = node_config["id"][1]

        if id_config == "column":

            # keep columns
            id_col = node_config["id"][2]

            ids = pd.read_csv(
                id_file,
                usecols=[id_col],
                sep=src_sep,
                index_col=False,
                quotechar=src_quotechar,
            )
            # make sure no null keys
            ids = ids.dropna(how="all", axis=0)
            ids = ids.dropna(subset=id_col, axis=0)

            ids = ids.drop_duplicates()
            ids = ids.rename(columns={id_col: out_node_ids})
            # labels column
            ids[out_node_labels] = node_naming

            node_list = ids.copy()

            if node_config["properties"]:

                for prop in node_config["properties"]:

                    prop_config = node_config["properties"][prop]

                    if isinstance(prop_config, list):
                        prop_src = config["source files"][prop_config[0]]
                        id_prop_cols = prop_config[1]

                        props = pd.read_csv(
                            prop_src,
                            usecols=id_prop_cols,
                            sep=src_sep,
                            index_col=False,
                            quotechar=src_quotechar,
                        )

                        # make sure no null keys
                        props = props.dropna(how="all", axis=0)
                        props = props.dropna(subset=id_prop_cols[0], axis=0)

                        props = props.drop_duplicates(subset=id_prop_cols[0])
                        props = props.rename(
                            columns={
                                id_prop_cols[0]: out_node_ids,
                                id_prop_cols[1]: prop,
                            }
                        )

                        node_list = pd.merge(
                            left=node_list,
                            right=props,
                            how="left",
                            left_on=out_node_ids,
                            right_on=out_node_ids,
                        )
                    elif isinstance(prop_config, str):
                        node_list[prop] = prop_config
                    else:
                        raise TypeError(
                            f"Must provide a list [<src_file_alias>, [<id_col>, <prop_col>]] or string value with proposed property: {prop_config}"
                        )

        elif id_config == "headers":

            # get column names to exclude
            excl_cols = node_config["id"][2]
            # get substrings to remove from all
            rm_strings = node_config["id"][3]

            ids = pd.read_csv(
                id_file, header=0, sep=src_sep, index_col=False, quotechar=src_quotechar
            ).head(
                0
            )  # don't need rest of rows

            ids = ids.drop(excl_cols, axis=1)
            # make sure no null keys
            # ids = ids.dropna(how='all',axis=0)
            # ids = ids.dropna(subset=id_col, axis=0)

            # transpose
            ids = ids.T.reset_index()

            # remove substrings
            temp_ids = ids["index"]
            for s in rm_strings:
                temp_ids = [row.replace(s, "") for row in temp_ids]
            # replace with new names
            ids["index"] = temp_ids

            # rename
            ids = ids.rename(columns={"index": out_node_ids})
            # dropping dupes
            ids = ids.drop_duplicates()
            ids = ids.reset_index(drop=True)

            # add labels column
            ids[out_node_labels] = node_naming

            node_list = ids.copy()

            if node_config["properties"]:

                for prop in node_config["properties"]:

                    prop_config = node_config["properties"][prop]

                    if isinstance(prop_config, list):
                        prop_src = config["source files"][prop_config[0]]
                        id_prop_cols = prop_config[1]

                        props = pd.read_csv(
                            prop_src,
                            usecols=id_prop_cols,
                            sep=src_sep,
                            index_col=False,
                            quotechar=src_quotechar,
                        )

                        # make sure no null keys
                        props = props.dropna(how="all", axis=0)
                        props = props.dropna(subset=id_prop_cols[0], axis=0)

                        props = props.drop_duplicates(subset=id_prop_cols[0])
                        props = props.rename(
                            columns={
                                id_prop_cols[0]: out_node_ids,
                                id_prop_cols[1]: prop,
                            }
                        )

                        node_list = pd.merge(
                            left=node_list,
                            right=props,
                            how="left",
                            left_on=out_node_ids,
                            right_on=out_node_ids,
                        )
                    elif isinstance(prop_config, str):
                        node_list[prop] = prop_config
                    else:
                        raise TypeError(
                            f"Must provide a list [<src_file_alias>, [<id_col>, <prop_col>]] or string value with proposed property: {prop_config}"
                        )

        # saving the node list
        # first preparing header and data filenames
        filename_start = f'{out_prefix}_node_{node}_{node_config["id"][0]}'
        header_fname = f"{filename_start}-header.csv"
        data_fname_prefix = f"{filename_start}-data"
        # preparing header and data file output paths
        header_fpath = os.path.join(out_fpath, header_fname)
        data_fpath_start = os.path.join(out_fpath, data_fname_prefix)
        # for now no multi_csv option .....
        current_data_fname = data_fpath_start + "1.csv"

        # cypher formatting?
        if out_cypher:
            # for nodes
            # camelCase property names
            node_list = node_list.rename(
                columns=lambda x: (
                    cypher_camelcase(x, lower_first=True)
                    if x not in [out_node_ids, out_node_labels]
                    else x
                )
            )

        if out_sep_header:
            # WRITING DATA FILE
            node_list.to_csv(
                current_data_fname, mode="w", header=False, index=False, sep=out_sep
            )
            # WRITING HEADER FILE
            # write header to header file
            node_list.head(0).to_csv(
                header_fpath, mode="w", header=True, index=False, sep=out_sep
            )
        else:
            node_list.to_csv(
                current_data_fname, mode="w", header=True, index=False, sep=out_sep
            )

    # now making the edge lists

    for edge in config["edges"]:

        logger.info(f"Creating {edge} list...")

        edge_naming = re.sub(r"[^A-Za-z]+$", "", edge)

        # get params
        edge_config = config["edges"][edge]
        fname = config["source files"][edge_config["from"][0]]
        is_edge_list = edge_config["from"][1]
        src_nodes = edge_config["src"]
        target_nodes = edge_config["target"]

        if is_edge_list:

            node_cols = edge_config["from"][2]
            all_cols = node_cols.copy()
            src_col = node_cols[0]
            target_col = node_cols[1]

            renames = {src_col: out_start_ids, target_col: out_end_ids}
            new_static_props = {}

            if edge_config["properties"]:

                for prop in edge_config["properties"]:

                    prop_config = edge_config["properties"][prop]

                    if isinstance(prop_config, list):
                        prop_src = config["source files"][prop_config[0]]
                        id_prop_cols = prop_config[1]
                        all_cols += id_prop_cols
                        renames[id_prop_cols[0]] = prop
                    elif isinstance(prop_config, str):
                        new_static_props[prop] = prop_config
                    else:
                        raise TypeError(
                            f"Must provide a list [<src_file_alias>, [<id_col>, <prop_col>]] or string value with proposed property: {prop_config}"
                        )

            # init edge list
            df = pd.read_csv(
                fname,
                usecols=all_cols,
                sep=src_sep,
                header=0,
                index_col=False,
                quotechar=src_quotechar,
            )
            # make sure no null keys
            df = df.dropna(how="all", axis=0)
            df = df.dropna(subset=node_cols, axis=0)

            df = df.drop_duplicates()
            df = df.rename(columns=renames)
            # labels column
            df[out_edge_labels] = edge_naming

            # adding static props
            for property in new_static_props:
                # populate values in a column
                df[property] = new_static_props[property]

            new_edge_list = df

            # saving the edge list
            # first preparing header and data filenames
            filename_start = f'{out_prefix}_edge_{edge}_{src_nodes}_{"".join(e for e in target_nodes if e.isalnum())}_{edge_config["from"][0]}'
            header_fname = f"{filename_start}-header.csv"
            data_fname_prefix = f"{filename_start}-data"
            # preparing header and data file output paths
            header_fpath = os.path.join(out_fpath, header_fname)
            data_fpath_start = os.path.join(out_fpath, data_fname_prefix)
            # for now no multi_csv option .....
            current_data_fname = data_fpath_start + "1.csv"

            # cypher formatting?
            if out_cypher:
                try:
                    # UPPER_CASE edge labels
                    new_edge_list[out_edge_labels] = new_edge_list[
                        out_edge_labels
                    ].apply(cypher_upper)
                except Exception:
                    logger.info(
                        f"UPPER_CASE of {out_edge_labels} not completed. \
                        May be due to labels not in this csv - column names: {new_edge_list.columns}"
                    )
                # camelCase property names
                new_edge_list = new_edge_list.rename(
                    columns=lambda x: (
                        cypher_camelcase(x, lower_first=True)
                        if x not in [out_start_ids, out_end_ids, out_edge_labels]
                        else x
                    )
                )

            if out_sep_header:
                # WRITING DATA FILE
                new_edge_list.to_csv(
                    current_data_fname, mode="w", header=False, index=False, sep=out_sep
                )
                # WRITING HEADER FILE
                new_edge_list.head(0).to_csv(
                    header_fpath, mode="w", header=True, index=False, sep=out_sep
                )
            else:
                new_edge_list.to_csv(
                    current_data_fname, mode="w", header=True, index=False, sep=out_sep
                )

        else:
            source_col = edge_config["from"][2]
            excl_cols = edge_config["from"][3]
            rm_strings = edge_config["from"][4]
            keepers = edge_config["keep_values"][0]
            attr_col_name = edge_config["keep_values"][1]
            evi_col_name = edge_config["keep_values"][2]

            df = pd.read_csv(
                fname, header=0, index_col=False, sep=src_sep, quotechar=src_quotechar
            )

            # will need target nodes
            # get node list (only need columns dont need rest of rows for this)
            nodes = df.head(0).drop(source_col, axis=1).T.reset_index()
            # get rid of excl columns (source_col should not be in this list)
            # but just in case
            nodes = nodes.drop([x for x in excl_cols if x != source_col], axis=1)
            # remove substrings
            temp_ids = nodes["index"]
            for s in rm_strings:
                temp_ids = [row.replace(s, "") for row in temp_ids]
            # replace with new names
            nodes["index"] = temp_ids
            nodes = nodes.drop_duplicates()
            nodes = nodes.reset_index(drop=True)

            # making each edge list
            for node in nodes["index"]:

                # save subset as own df
                edge_list = df[
                    [source_col] + [col for col in df.columns if node in col]
                ].copy()
                # rename column names
                edge_list.columns = [
                    x.replace(node, "").strip("_") for x in edge_list.columns
                ]
                # add target node column
                edge_list[out_end_ids] = node
                # edge type
                edge_list[out_edge_labels] = edge_naming

                # filter rows
                filtered = (
                    edge_list[
                        (edge_list.isin(keepers)).any(
                            axis=1
                        )  # keep rows where has Positive or Negative in a column
                    ]
                    .reset_index(drop=True)
                    .copy()
                )
                # init new columns
                filtered[attr_col_name] = ""
                filtered[evi_col_name] = ""

                # temp flag where null all other values except for Positive or Negative
                temp_mask = filtered[(filtered.isin(keepers))]

                for x in np.arange(len(temp_mask)):

                    # put positive or negative in has_attr column
                    attr = list(set(temp_mask.iloc[x, :].dropna().values))
                    assert len(attr) == 1, f"{attr} should only match one in {keepers}"
                    filtered.at[x, attr_col_name] = attr[0]
                    # which evidence types support
                    evi = list((temp_mask.iloc[x, :].dropna().index))

                    if evi != [""]:
                        filtered.at[x, evi_col_name] = evi

                # drop other unnecessary columns in edge list
                if (filtered[evi_col_name] == "").all():
                    edge_list = filtered[
                        [source_col, out_end_ids, attr_col_name, out_edge_labels]
                    ]
                else:
                    edge_list = filtered[
                        [
                            source_col,
                            out_end_ids,
                            attr_col_name,
                            evi_col_name,
                            out_edge_labels,
                        ]
                    ]

                # change source column naming
                new_edge_list = edge_list.rename(columns={source_col: out_start_ids})

                # adding option to add static properties ONLY
                if edge_config["properties"]:

                    for prop in edge_config["properties"]:

                        id_prop_cols = edge_config["properties"][prop]

                        if isinstance(id_prop_cols, list):
                            raise TypeError(
                                f"Must provide a string value with proposed property: {edge_config}"
                            )
                        elif isinstance(id_prop_cols, str):
                            new_edge_list[prop] = id_prop_cols
                        else:
                            raise TypeError(
                                f"Must provide a string value with proposed property: {edge_config}"
                            )

                # saving the edge list
                # first preparing header and data filenames
                filename_start = f'{out_prefix}_edge_{edge}_{src_nodes}_{node}_{edge_config["from"][0]}'
                header_fname = f"{filename_start}-header.csv"
                data_fname_prefix = f"{filename_start}-data"
                # preparing header and data file output paths
                header_fpath = os.path.join(out_fpath, header_fname)
                data_fpath_start = os.path.join(out_fpath, data_fname_prefix)
                # for now no multi_csv option .....
                current_data_fname = data_fpath_start + "1.csv"

                # cypher formatting?
                if out_cypher:
                    try:
                        # UPPER_CASE edge labels
                        new_edge_list[out_edge_labels] = new_edge_list[
                            out_edge_labels
                        ].apply(cypher_upper)
                    except Exception:
                        logger.info(
                            f"UPPER_CASE of {out_edge_labels} not completed. \
                            May be due to labels not in this csv - column names: {new_edge_list.columns}"
                        )
                    # camelCase property names
                    new_edge_list = new_edge_list.rename(
                        columns=lambda x: (
                            cypher_camelcase(x, lower_first=True)
                            if x not in [out_start_ids, out_end_ids, out_edge_labels]
                            else x
                        )
                    )

                if out_sep_header:
                    # WRITING DATA FILE
                    new_edge_list.to_csv(
                        current_data_fname,
                        mode="w",
                        header=False,
                        index=False,
                        sep=out_sep,
                    )
                    # WRITING HEADER FILE
                    new_edge_list.head(0).to_csv(
                        header_fpath, mode="w", header=True, index=False, sep=out_sep
                    )
                else:
                    new_edge_list.to_csv(
                        current_data_fname,
                        mode="w",
                        header=True,
                        index=False,
                        sep=out_sep,
                    )

    # done statement
    logger.info("Run Complete.")

if __name__ == "__main__":

    ## GET ARGS
    args = get_args(
        prog_name="edge-list-builder",
        others=dict(
            description="makes node and edge property lists from other data csvs"
        ),
    )

    main(args.config)
