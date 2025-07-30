"""
The purpose of this script is to create a networkx graph from node and edge lists
And output a .graphml file

PLEASE NOTE: the data files and their matching header file must have the SAME
    filenaming except for the suffices of '-header.csv' and 'data.csv'
    OR '-header.csv' and 'data1.csv', 'data2.csv'
"""

import glob
import os
import re
import sys

import networkx as nx
import pandas as pd

# import modules
from gdbcore.helpers.utils import (
    config_loader,
    filter_filepaths,
    find_matches,
    get_args,
    get_logger,
)
from gdbcore.helpers.utils_nx import attach_header_to_data, create_tuples_list

if __name__ == "__main__":

    ## GET ARGS
    args = get_args(
        prog_name="nx-graph-builder",
        others=dict(
            description="builds a networkx graph (and .graphml file) from node and edge property lists"
        ),
    )

    ## START LOG FILE
    logger = get_logger()
    logger.info(f"Arguments: {args}")

    ## LOAD CONFIG PARAMETERS
    # getting the config filepath
    config_filepath = args.config
    # log it
    logger.info(f"Path to config file: {config_filepath}")
    # load config params
    logger.info("Loading config params ... ")
    config = config_loader(config_filepath)
    logger.info(config)

    node_folder = config["data sources"]["node lists"]
    edge_folder = config["data sources"]["edge lists"]

    sep = config["data sources"]["sep"]
    sep_headers = config["data sources"]["header files"]
    node_ids = config["data sources"]["columns"]["node_ids"]
    node_type = config["data sources"]["columns"]["node_labels"]
    edge_type = config["data sources"]["columns"]["edge_labels"]
    start_ids = config["data sources"]["columns"]["start_ids"]
    end_ids = config["data sources"]["columns"]["end_ids"]

    graph_type = config["kg setup"]["graph type"]

    gt_path = config["graph-tool"]["path"]
    # found by running brew --prefix graph-tool
    sys.path.append(gt_path)
    import graph_tool.all as gt

    graphml_path = config["kg setup"]["graphml output"]

    ## GENERATE NX GRAPH
    # getting node and edge files
    node_files = filter_filepaths(node_folder, identifiers=["node"])
    edge_files = filter_filepaths(edge_folder, identifiers=["edge"])
    # print
    logger.info(node_files)
    logger.info(edge_files)

    # init graph
    graph_mapping = {
        "MultiDiGraph": nx.MultiDiGraph(),
        "Graph": nx.Graph(),
        "DiGraph": nx.DiGraph(),
        "MultiGraph": nx.MultiGraph(),
    }
    G = graph_mapping[graph_type]

    # adding nodes to the graph
    # if separate header files we need to attach the column names/header to the data file first
    if sep_headers:

        logger.info("Attaching headers to node data files")

        # separating header and data files into sep lists
        node_header_files = filter_filepaths(node_files, identifiers=["-header.csv"])
        node_data_files = filter_filepaths(node_files, identifiers=["-data"])

        # going through each data file
        for file in node_data_files:
            # finding matching header file
            matching_header = find_matches(filepath=file, area=node_header_files)

            assert (
                len(matching_header) == 1
            ), f"{file} should only have one matching header file: {matching_header}"

            # attach header to datafile
            df_nodes = attach_header_to_data(
                data_path=file, header_path=matching_header[0], sep=sep
            )

            # this function transforms the data so ready to pass to nx
            node_info = create_tuples_list(df_nodes, [node_ids])

            # now adding the nodes to the graph
            G.add_nodes_from(node_info)

    # if the csvs have column names already attached (no separate header files)
    else:

        for file in node_files:
            # read in
            df_nodes = pd.read_csv(file, sep=sep, low_memory=False)
            # transform so ready to pass to nx
            node_info = create_tuples_list(df_nodes, [node_ids])
            # add nodes
            G.add_nodes_from(node_info)

    # verbosity
    logger.info(f"{G.number_of_nodes()} nodes added to nx graph.")

    # adding edges to the graph
    if sep_headers:

        logger.info("Attaching headers to edge data files")
        edge_header_files = filter_filepaths(edge_files, identifiers=["-header.csv"])
        edge_data_files = filter_filepaths(edge_files, identifiers=["-data"])

        for file in edge_data_files:

            # finding matching header file
            matching_header = find_matches(filepath=file, area=edge_header_files)

            assert (
                len(matching_header) == 1
            ), f"{file} should only have one matching header file: {matching_header}"

            # attach header to datafile
            df_edges = attach_header_to_data(
                data_path=file, header_path=matching_header[0], sep=sep
            )

            # transform so ready to pass to nx
            edge_info = create_tuples_list(df_edges, [start_ids, end_ids])
            print(edge_info)
            G.add_edges_from(edge_info)

    else:

        for file in edge_files:

            df_edges = pd.read_csv(file, sep=sep, low_memory=False)

            # transform so ready to pass to nx
            edge_info = create_tuples_list(df_edges, [start_ids, end_ids])
            print(edge_info)
            G.add_edges_from(edge_info)

    # verbosity
    logger.info(f"{G.number_of_edges()} edges added to nx graph.")

    # writing nx graph to graphml output file
    logger.info(f"Writing to graphml file: {graphml_path}")

    # changing edge ids
    for u, v, k in G.edges(keys=True):
        G[u][v][k]["id"] = k

    nx.write_graphml(G, graphml_path, named_key_ids=True)

    # logit
    logger.info("Run Complete")

else:
    print("File imported instead of executed. Not completed.")
