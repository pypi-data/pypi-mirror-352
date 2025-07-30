# main purpose is for getting nx to graphml
# but really can be used for other nx things
import os
import re

import networkx as nx
import pandas as pd

from gdbcore.helpers.utils import assert_path, filter_filepaths


def create_tuples_list(df: pd.DataFrame, id_cols: list) -> list:
    """
    Transform given df into list of tuples where:
    - each node represented by a tuple like this: (node_id, dict_of_node_attributes)
    - each edge repped by a tuple like this: (start_id, end_id, dict_of_edge_attributes)

    PARAMS
    -----
    - df (pandas.DataFrame): a dataframe holding a node or edge list
    - id_cols (list): a list of the columns in the df that hold the node/edge ids

    OUTPUTS
    -----
    - list_df (list): each node/edge as a tuple in a list

    EXAMPLE
    -----
    TODO
    """

    # PRECONDITIONS
    assert isinstance(df, pd.DataFrame), "df must be a pandas dataframe"
    assert isinstance(id_cols, list), f"id_cols must be a list {id_cols}"
    for id in id_cols:
        assert id in df.columns, f"{id} not in df columns: {df.columns}"

    # MAIN FUNCTION
    # put the id_cols contents (as a Series) in a list
    args = [df[col] for col in id_cols]
    # also adding to list the rest of the data but as a dictionary
    args.append(df.drop(id_cols, axis=1).to_dict("records"))

    # now turning them into a list of tuples
    list_df = list(zip(*args))

    # POSTCONDITIONS
    assert len(list_df) == len(
        df
    ), f"number of tuples {len(list_df)} does not match df length {len(df)}"

    return list_df


def attach_header_to_data(
    data_path: str, header_path: str, sep: str = ","
) -> pd.DataFrame:
    """
    - Reads in datafile and matching header file as pd.Dataframes
    - and attaches the header as the df columns

    PARAMS
    -----
    - data_path (str): the (ideally) absolute filepath to the datafile
    - header_path (str): the absolute filepath to the corresponding header file
    - sep (str): delimiter

    OUTPUTS
    -----
    - df (pd.DataFrame): The datafile as df with header as column names

    EXAMPLE
    -----
    TODO

    """

    # PRECONDITIONS
    assert_path(data_path)
    assert_path(header_path)
    assert isinstance(sep, str), f"sep must be given as a string {sep}"

    # MAIN FUNCTION
    # read in the datafile
    df = pd.read_csv(data_path, sep=sep, header=None, low_memory=False)
    # read in the header
    df_header = pd.read_csv(header_path, sep=sep)
    # attach header
    df.columns = df_header.columns

    return df
