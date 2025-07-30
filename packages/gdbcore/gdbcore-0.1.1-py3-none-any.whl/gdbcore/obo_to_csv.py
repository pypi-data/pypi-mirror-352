"""
The purpose of this script is to create initial node and edge lists as csvs
    from the OBO files in config/config.yaml.
Any additional cleaning of the node and edge lists can be done 
    by reading in those csvs (e.g., as pandas dataframes) and then re-saving as csv. 

PLEASE NOTE: the data files and their matching header file must have the SAME
    filenaming except for the suffices of '-header.csv' and 'data.csv'
    OR '-header.csv' and 'data1.csv', 'data2.csv'
"""

# import modules
from gdbcore.helpers.utils import (
    get_args,
    get_logger,
    config_loader,
    assert_path,
    assert_nonempty_keys,
    assert_nonempty_vals,
)
from gdbcore.helpers.utils_obonet import (
    convertOBOtoNet,
    get_node_subgraphs,
    generate_node_files,
    generate_edge_files,
)


if __name__ == "__main__":

    ## GET ARGS
    args = get_args(
        prog_name="obo-to-csv",
        others=dict(description="turns obo files into node and edge property lists"),
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
    logger.info(f"Configuration: {config}")
    # obo files
    obos = config["ontologies"]["obo"]
    # output file params
    # filepath
    outpath = config["output"]["folder path"]
    assert_path(outpath)
    # additional out params
    out_prefix = config["output"]["prefix"]
    out_sep_header = config["output"]["separate header"]
    sep = config["output"]["sep"]
    quotechar = config["output"]["quotechar"]
    fill_na = config["output"]["fill_na"]
    # column names corresponding to
    assert_nonempty_keys(config["output"]["col_names"])
    assert_nonempty_vals(config["output"]["col_names"])
    # init col_names dicts for column renaming based on output > col_names
    node_col_names = {
        "node_ids": config["output"]["col_names"]["node_ids"],
        "node_labels": config["output"]["col_names"]["node_labels"],
    }
    edge_col_names = {
        "edge_labels": config["output"]["col_names"]["edge_labels"],
        "start_ids": config["output"]["col_names"]["start_ids"],
        "end_ids": config["output"]["col_names"]["end_ids"],
    }
    # additional db specific formating (TODO)
    # out_cypher = config['output']['cypher_formatting']

    ## GENERATE NODE AND EDGE LISTS AS CSVs FROM THE OBOs in config.yaml
    for obo in obos:
        # create networkx graph
        G = convertOBOtoNet(obos[obo]["path"])
        # log it
        logger.info(f"Converting {obo} from {obos[obo]['path']} to networkx")

        # if label provided, or if labels exist in a nx node attribute e.g. namespace for GeneOnt
        if "label" in obos[obo].keys():
            subgraphs = get_node_subgraphs(
                graph=G, by_attribute=False, assign_label=obos[obo]["label"]
            )
        elif "labels in" in obos[obo].keys():
            subgraphs = get_node_subgraphs(graph=G, by_attribute=obos[obo]["labels in"])
        else:
            raise ValueError(f'No "label" or "labels in" provided in config at {obo}.')

        # creating dfs
        # log it
        logger.info(f"Converting {obo} from nx graph to df and saving to {outpath}")
        # node lists
        generate_node_files(
            subgraph_dict=subgraphs,
            prefix=f"{out_prefix}_{obo}_nodes",
            folderpath=outpath,
            sep=sep,
            quotechar=quotechar,
            fill_na=fill_na,
            sep_header=out_sep_header,
            col_names=node_col_names,
        )
        # edge lists
        generate_edge_files(
            graph=G,
            prefix=f"{out_prefix}_{obo}_edges",
            folderpath=outpath,
            sep=sep,
            quotechar=quotechar,
            fill_na=fill_na,
            sep_header=out_sep_header,
            col_names=edge_col_names,
        )
    # logit
    logger.info("Run Complete")

else:
    print("File imported instead of executed. Not completed.")
