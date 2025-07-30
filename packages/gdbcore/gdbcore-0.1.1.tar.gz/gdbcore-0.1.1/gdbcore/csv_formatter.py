"""
The purpose of this script is to take node and edge lists (separate files) and create initial node and edge lists as csvs

Options to rename mandatory columns and remove some columns.

Any additional cleaning of the node and edge lists can be done any way you prefer outside of this script. 

Requirements:
- node and edge lists should be separated csvs
- don't have excess files in the src foldr
- filenaming:
    - if source files have a separate header the corresponding header should have '-header' in the filename

"""

# imports
import os
import pandas as pd

# import modules
from gdbcore.helpers.utils import (
    get_args,
    get_logger,
    config_loader,
    filter_filepaths,
    get_line_count,
    warn_folder,
    assert_nonempty_keys,
    assert_nonempty_vals,
    group_files,
    find_matches,
    get_header,
)
from gdbcore.helpers.utils_nelist import IntSorter
from gdbcore.helpers.utils_cypher import cypher_upper, cypher_camelcase


if __name__ == "__main__":

    ## GET ARGS
    args = get_args(
        prog_name="csv-formatter",
        others=dict(description="not sure anymore"),
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

    # assign to variables for use in script
    chunksize = config["chunksize"]
    # incoming file conditions
    src_fpath = config["source"]["folder path"]
    src_sep_header = config["source"]["separate header"]
    src_multi_csv = config["source"]["multi_csv"]
    src_sep = config["source"]["sep"]
    src_quotechar = config["source"]["quotechar"]
    # column names corresponding to
    assert_nonempty_keys(config["source"]["col_names"])
    assert_nonempty_vals(config["source"]["col_names"])
    src_node_ids = config["source"]["col_names"]["node_ids"]
    src_node_labels = config["source"]["col_names"]["node_labels"]
    src_edge_labels = config["source"]["col_names"]["edge_labels"]
    src_start_ids = config["source"]["col_names"]["start_ids"]
    src_end_ids = config["source"]["col_names"]["end_ids"]
    src_exclude_cols = config["source"]["col_names"]["exclude list"]
    # outcoming file settings
    out_fpath = config["output"]["folder path"]
    out_prefix = config["output"]["prefix"]
    out_sep_header = config["output"]["separate header"]
    out_multi_csv = config["output"]["multi_csv"]
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
    out_max_rows = config["output"]["max_rows"]
    # additional db specific formating
    out_cypher = config["output"]["cypher_formatting"]

    # warning
    message = f"""
            Warning: There are existing files in the output path {out_fpath}. 
            There is a risk of duplicating nodes and edges being appended to these files.
            """
    logger.info(warn_folder(folderpath=out_fpath, warning_message=message))

    # getting filepaths
    datafiles = filter_filepaths(
        src_fpath, identifiers=[".csv"], exclude=["-header", ".graphml"]
    )
    headfiles = filter_filepaths(
        src_fpath, identifiers=["-header", ".csv"], exclude=[".graphml"]
    )

    # grouping them to accomodate multi_csv (this may not be necessary anymore)

    grouped_files = group_files(
        source_folder=datafiles,
        sub=("\d*.csv", ""),
    )
    logger.info(group_files)

    # node files first
    for group in grouped_files:

        # get the group of files
        filelist = grouped_files[group]
        logger.info(filelist)

        # get the original base filename
        og_fname = os.path.splitext(os.path.basename(group))[0]

        # preparing the new filenames
        filename_start = f"{out_prefix}_{og_fname}"
        logger.info(filename_start)

        # preparing header and data filenames
        header_fname = f"{filename_start}-header.csv"
        data_fname_prefix = f"{filename_start}-data"
        # preparing header and data file output paths
        header_fpath = os.path.join(out_fpath, header_fname)
        data_fpath_start = os.path.join(out_fpath, data_fname_prefix)

        for file in filelist:

            logger.info(f"Searching {file} ...")

            # if the source files have separate header files
            if src_sep_header:
                # get the matching header
                header_file = find_matches(file, area=headfiles)
                header = get_header(
                    header_file[0], sep=src_sep, quotechar=src_quotechar
                )

                reader = pd.read_csv(
                    file,
                    names=[x for x in header if x not in src_exclude_cols],
                    chunksize=chunksize,
                    sep=src_sep,
                    usecols=lambda x: x not in src_exclude_cols,
                )
            # otherwise don't attach header
            else:
                reader = pd.read_csv(
                    file,
                    header=0,
                    chunksize=chunksize,
                    sep=src_sep,
                    usecols=lambda x: x not in src_exclude_cols,
                )

            for chunk in reader:

                if out_multi_csv:
                    # getting the latest data file
                    # first get all data files for that node/edge type
                    data_list = filter_filepaths(
                        fpath=out_fpath, identifiers=[data_fname_prefix]
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
                        if get_line_count(latest_fname) >= out_max_rows:
                            current_data_fname = (
                                f"{data_fpath_start}{latest_fnum + 1}.csv"
                            )
                            print(f"Creating {current_data_fname}...")
                        else:
                            current_data_fname = latest_fname
                    else:
                        # if no data files create the first one
                        current_data_fname = f"{data_fpath_start}1.csv"
                        print(f"Creating {current_data_fname}...")
                else:
                    # if not writing node/edges to multiple csvs, then use suffix 1 always
                    current_data_fname = f"{data_fpath_start}1.csv"

                # prep rename dict
                src_v_out = {
                    src_node_ids: out_node_ids,
                    src_node_labels: out_node_labels,
                    src_edge_labels: out_edge_labels,
                    src_start_ids: out_start_ids,
                    src_end_ids: out_end_ids,
                }
                # rename columns?
                chunk = chunk.rename(columns=src_v_out)

                # cypher formatting?
                if out_cypher:
                    # for nodes
                    try:
                        # CamelCase node labels
                        chunk[out_node_labels] = chunk[out_node_labels].apply(
                            cypher_camelcase,
                            lower_first=False,
                        )
                    except Exception:
                        logger.info(
                            f"CamelCase of {out_node_labels} not completed. May be due to labels not in this csv - column names: {chunk.columns}"
                        )
                    # for edges
                    try:
                        # UPPER_CASE edge labels
                        chunk[out_edge_labels] = chunk[out_edge_labels].apply(
                            cypher_upper
                        )
                    except Exception:
                        logger.info(
                            f"UPPER_CASE of {out_edge_labels} not completed. May be due to labels not in this csv - column names: {chunk.columns}"
                        )
                    # camelCase property names
                    chunk = chunk.rename(
                        columns=lambda x: (
                            cypher_camelcase(x, lower_first=True)
                            if x not in src_v_out.values()
                            else x
                        )
                    )

                # append to outfiles
                if out_sep_header:
                    chunk.to_csv(
                        current_data_fname,
                        mode="a",
                        header=False,
                        index=False,
                        sep=out_sep,
                    )
                    # WRITING HEADER FILE
                    # checking if header already exists
                    if (os.path.exists(header_fpath) == False) or get_line_count(
                        header_fpath
                    ) < 1:
                        # if doesn't exist then create it
                        logger.info(f"Creating {header_fpath}...")
                        # write header to header file
                        chunk.head(0).to_csv(
                            header_fpath,
                            mode="w",
                            header=True,
                            index=False,
                            sep=out_sep,
                        )
                else:
                    chunk.to_csv(
                        current_data_fname,
                        mode="a",
                        header=True,
                        index=False,
                        sep=out_sep,
                    )

    # done statement
    logger.info("Run Complete.")

else:
    print("File imported instead of executed. Not completed.")
