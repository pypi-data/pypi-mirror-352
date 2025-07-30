"""
The purpose of this script is to take a neo4j dump file and create initial node and edge lists as csvs

Empty columns are removed as well.

Any additional cleaning of the node and edge lists can be done any way you prefer
    by reading in those csvs (e.g., as pandas dataframes) and then re-saving as csv. 
"""

# imports
import os
import pandas as pd

# import modules
from gdbcore.helpers.utils import (
    config_loader,
    copy_recursively,
    filter_filepaths,
    get_args,
    get_logger,
    filter_filepaths,
    get_line_count,
    warn_folder,
    assert_nonempty_keys,
    assert_nonempty_vals,
    assert_path,
)
from gdbcore.helpers.utils_nelist import (
    generate_nelist_basefname,
    IntSorter,
    rm_empty_col,
    group_nelist_files,
)


if __name__ == "__main__":

    ## GET ARGS
    args = get_args(
        prog_name="neo4j_dump_to_proplists",
        others=dict(
            description="Takes a Neo4j dump file and turns it into node and edge property lists"
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
    assert_nonempty_keys(config)
    assert_nonempty_vals(config)
    logger.info(f"Configuration: {config}")

    # fpaths
    input_fpath = config["generate ne lists"]["filepaths"]["input_file"]
    assert_path(input_fpath)
    ne_output_folder = config["generate ne lists"]["filepaths"]["output_folder"]
    try:
        assert_path(ne_output_folder)
    except:
        os.mkdir(ne_output_folder)
        logger.info(f"{ne_output_folder} created.")

    # column names corresponding to
    assert_nonempty_keys(config["generate ne lists"]["col_names"])
    assert_nonempty_vals(config["generate ne lists"]["col_names"])
    node_ids = config["generate ne lists"]["col_names"]["node_ids"]
    node_labels = config["generate ne lists"]["col_names"]["node_labels"]
    edge_labels = config["generate ne lists"]["col_names"]["edge_labels"]
    start_ids = config["generate ne lists"]["col_names"]["start_ids"]
    end_ids = config["generate ne lists"]["col_names"]["end_ids"]

    input_sep = config["generate ne lists"]["input_sep"]
    output_sep = config["generate ne lists"]["output_sep"]
    quotechar = config["generate ne lists"]["quotechar"]

    prefix = config["generate ne lists"]["db_name"]
    max_rows = config["generate ne lists"]["max_rows"]
    multi_csv = config["generate ne lists"]["multi_csvs"]

    chunksize = config["generate ne lists"]["chunksize"]
    skip_to = config["generate ne lists"]["skip_to_row"]
    skip_to_chunk = skip_to // chunksize
    cleaned_prefix = "clean"
    # how many rows in dump file
    len_dump = get_line_count(input_fpath)
    num_chunks = len_dump // chunksize
    logger.info(f"There are {len_dump} rows in the dump file. {num_chunks} expected.")

    # warning
    message = f"""
            Warning: There are existing files in the output path {ne_output_folder}. 
            There is a risk of duplicating nodes and edges being appended to these files.
            """
    logger.info(warn_folder(folderpath=ne_output_folder, warning_message=message))

    # init node and edge lists, by going line by line through dump file

    # PREP WORK
    reader = pd.read_csv(input_fpath, chunksize=chunksize, sep=input_sep)

    # counter for skip to option and test
    counter = 0

    for df in reader:
        if counter < skip_to_chunk:
            counter += 1
            logger.info(f"Chunk number: {counter}")
            logger.info(
                f"Skipping until row {skip_to} which is in chunk {skip_to_chunk}"
            )

        # for testing
        # elif counter > skip_to_chunk+10:
        #     print('end test')
        #     break

        else:
            # Isolating edges from df
            df_edges = df.dropna(subset=[edge_labels])
            # Isolating nodes from df
            df_nodes = df.dropna(subset=[node_labels])
            # making sub-dfs for each node/edge type
            all_edge_dfs = df_edges.groupby(edge_labels)
            all_node_dfs = df_nodes.groupby(node_labels)

            # putting them in dict with node/edge name as key and df as value
            all_groups = {n: all_node_dfs.get_group(n) for n in all_node_dfs.groups}
            all_groups.update(
                {e: all_edge_dfs.get_group(e) for e in all_edge_dfs.groups}
            )

            # append each to a csv
            for each_ne in all_groups:

                # remove cypher formating in name
                name = each_ne.strip(":")
                # df
                df = all_groups[each_ne]
                df = df.rename(
                    columns={
                        node_ids: "id:ID",
                        start_ids: ":START_ID",
                        end_ids: ":END_ID",
                        node_labels: ":LABEL",
                        edge_labels: ":TYPE",
                    }
                )
                # first check
                assert (
                    ":LABEL" in df.columns or ":TYPE" in df.columns
                ), f"header does not contain node or edge label column: {df.columns}"
                # get header
                header = df.head(0)

                # Init filenaming depending on node label / edge type
                # if edge labels are empty then a node
                if df[":TYPE"].isnull().all():
                    filename_start = generate_nelist_basefname(
                        filetype="nodes", label=name, prefix=prefix
                    )
                elif df[":LABEL"].isnull().all():
                    filename_start = generate_nelist_basefname(
                        filetype="edges", label=name, prefix=prefix
                    )
                else:
                    raise ValueError(f"Issue with node/edge labels for {each_ne}")

                # preparing header and data filenames
                header_fname = f"{filename_start}-header.csv"
                data_fname_prefix = f"{filename_start}-data"
                # preparing header and data file output paths
                header_fpath = os.path.join(ne_output_folder, header_fname)
                data_fpath_start = os.path.join(ne_output_folder, data_fname_prefix)

                # WRITING HEADER FILE
                # checking if header already exists
                if (os.path.exists(header_fpath) == False) or get_line_count(
                    header_fpath
                ) < 1:
                    # if doesn't exist then create it
                    logger.info(f"Creating {header_fpath}...")
                    # write header to header file
                    header.to_csv(
                        header_fpath, mode="w", header=True, index=False, sep=output_sep
                    )
                # else:
                #     logger.info(f'{header_fpath} already exists.')

                # NOW WRITING NODE/EDGE TO NEWEST/LATEST DATA FILE

                # for multi csvs
                if multi_csv:
                    # getting the latest data file
                    # first get all data files for that node/edge type
                    data_list = filter_filepaths(
                        fpath=ne_output_folder, identifiers=[data_fname_prefix]
                    )

                    if len(data_list) > 0:
                        # sort by digit suffix using utils.IntSorter
                        dl_sorter = IntSorter(
                            regex=f"{data_fpath_start}(\d+).csv", default_val=0
                        )
                        # getting the latest file (biggest digit suffix)
                        sorted_dl = dl_sorter.sort(
                            a_list=data_list,
                            num_reverse=True,
                            str_reverse=False,
                            str_lower=False,
                        )
                        latest_fname = sorted_dl[0]
                        # what's the latest file number?
                        latest_fnum = dl_sorter.get_int(latest_fname)

                        # create a new file if the latest file reaches max_rows
                        if get_line_count(latest_fname) >= max_rows:
                            current_data_fname = (
                                f"{data_fpath_start}{latest_fnum + 1}.csv"
                            )
                            logger.info(f"Creating {current_data_fname}...")
                        else:
                            current_data_fname = latest_fname
                    else:
                        # if no data files create the first one
                        current_data_fname = f"{data_fpath_start}1.csv"
                        logger.info(f"Creating {current_data_fname}...")
                else:
                    # if not writing node/edges to multiple csvs, then use suffix 1 always
                    current_data_fname = f"{data_fpath_start}1.csv"

                # append node/edge data to the current fname
                df.to_csv(
                    current_data_fname,
                    mode="a",
                    header=False,
                    index=False,
                    sep=output_sep,
                )

                # verbose
                logger.info(
                    f"Chunk Number{counter}, Row Num{chunksize*counter}: {current_data_fname} has {get_line_count(current_data_fname)} lines."
                )

            counter += 1

    # DONE WRITING THE INIT NODE AND EDGE FILES FROM DUMP
    data_files = filter_filepaths(
        ne_output_folder, identifiers=["-data"], exclude=[cleaned_prefix]
    )
    # group the data_files
    grouped_files = group_nelist_files(
        source_folder=ne_output_folder, exclude_files_with=["-header", cleaned_prefix]
    )
    # verbose
    for group in grouped_files:
        logger.info(f"{group} created with files: {grouped_files[group]}")

    # NOW REMOVING EMPTY COLUMNS
    # make sure any old cleaned files are not in the folder
    for group in grouped_files:
        rm_empty_col(
            filelist=grouped_files[group],
            sep=output_sep,
            chunk_size=chunksize,
            prefix=cleaned_prefix,
        )
    # verbose
    clean_data_files = filter_filepaths(
        ne_output_folder, identifiers=["-data", cleaned_prefix]
    )
    for file in clean_data_files:
        logger.info(f"{file} created with {get_line_count(file)} lines.")

else:
    print("File imported instead of executed. Not completed.")
