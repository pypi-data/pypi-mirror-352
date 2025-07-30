# functions for formating node and edge lists
import os
import re

import pandas as pd

from gdbcore.helpers.utils import assert_path, filter_filepaths


def generate_nelist_basefname(
    filetype: str,
    label: str,
    prefix: str = "",
) -> str:
    """
    Creates node/edge (ne) list filenames

    PARAMETERS
    -----
    filetype (str): 'nodes' or 'edges'
    label (str): the node or edge label/type
    prefix (str): anything else to add to the fname i.e., db_name

    RETURNS
    -----
    filename (str): the node/edge filename (without -header.csv and -data.csv)

    EXAMPLES
    -----
    1)
    >>> generate_nelist_basefname('nodes', 'Disease', 'ckg')
    ckg_nodes_Disease
    2)
    >>> generate_nelist_basefname('edges', 'IS_A')
    edges_IS_A
    """
    # PRECONDITIONS
    # assert isinstance(dest_folder, str), 'folder must be a string'
    # assert os.path.exists(os.path.abspath(dest_folder)), \
    #     f'filepath does not exist: {os.path.abspath(dest_folder)}'
    assert (
        filetype == "nodes" or filetype == "edges"
    ), f'filetype must be "nodes" or "edges": {filetype}'
    assert isinstance(label, str), "label must be a string"
    assert isinstance(prefix, str), "prefix must be a string"

    # MAIN FUNCTION
    if prefix:
        filename = f"{prefix}_{filetype}_{label}"
    else:
        filename = f"{filetype}_{label}"

    return filename


class IntSorter:
    """
    - Takes a regex pattern to allow sorting by specified digits.
    - If regex not specified:
        - Will consider all items in the list with digits
    - Note: regardless of regex, will only ever take the first re.findall result
    - set default value higher than length of the list
    - if wanting non-numeric items to show up at end of sorted list:
        set default_val > len(list)
    - if wanting non-numeric items to show up first:
        default_val = -1
    (this spiraled out of control)
    """

    def __init__(self, regex: str = "\d+", default_val: int = -1):
        self.regex = regex
        self.default_val = default_val

    def get_int(self, item):
        """
        Returns a value that matches the regex or returns -1
        """
        val = self.default_val

        # get all regex results
        result = re.findall(self.regex, item)

        if len(result) > 0:
            try:
                val = int(result[0])
            except:
                pass
        return val

    def sort(
        self,
        a_list: list,
        num_reverse: bool = False,
        str_reverse: bool = False,
        str_lower: bool = False,
    ):
        """
        Takes a list and sorts it
        """
        if str_lower:
            case_list = [str(x).lower() for x in a_list]
        else:
            case_list = a_list.copy()
        alpha_sort = sorted(case_list, reverse=str_reverse)
        int_sort = sorted(alpha_sort, key=self.get_int, reverse=num_reverse)

        return int_sort


def group_nelist_files(
    source_folder: str, exclude_files_with: None | list = None
) -> dict:
    """
    - In a given folder, groups the datafiles by node/edge type
    - Used to group multicsvs in a list for rm_empty_col()

    PARAMS
    -----
    - source_folder (str): path to folder with the datafiles
    - exclude_files_with (list): a list of strings for use in filter_filepaths(exclude=)

    OUTPUTS
    -----
    - grouped_files (dict): a dictionary of lists

    EXAMPLE
    -----
    >>> grouped = group_nelist_files(ne_output_folder, exclude_files_with=['clean', '-header'])
    """
    # PRECONDITIONS
    assert_path(source_folder)
    if exclude_files_with is not None:
        assert isinstance(
            exclude_files_with, list
        ), f"exclude_files_with must be a list of strings: {exclude_files_with}"
        for ex in exclude_files_with:
            assert isinstance(
                ex, str
            ), f"exclude_files_with must be a list of strings: {ex}"

    # MAIN FUNCTION
    # init dict
    grouped_files = {}
    # getting all data files
    data_files = filter_filepaths(
        source_folder, identifiers=["-data"], exclude=exclude_files_with
    )
    # isolating unique main file names
    file_groups = set([re.sub("-datab*\d*.csv", "", fname) for fname in data_files])
    # generate grouped lists
    for file in file_groups:
        grouped_files[file] = [f for f in data_files if f.startswith(file)]

    return grouped_files


def rm_empty_col(
    filelist: list, sep: str = ",", chunk_size: int = 10000, prefix: str = "clean"
):
    """
    - for a given list of datafile(s) (e.g., single csv or multiple csvs for a given node/edge type):
        - removes empty columns and also
        - removes the column name from the affiliated header file
        - save as new csv file versions with the given prefix
    - removes empty columns from node and edge files created with dump_to_nelists.py
    - requires that the associated header file has similar file naming

    PARAMS
    -----
    - file (str): -data#.csv filename to remove empty columns from
    - sep (str): the delimiter
    - chunk_size (int): number of rows in a chunk
    - prefix (str): prefix for the "cleaned" version of the data + header file

    OUTPUTS
    -----
    - no return
    - writes to new data and header csv files in the same folder location,
        but with the given filenaming prefix
    - as part of sanity check prints out some statements

    """
    # PRECONDITIONS
    assert isinstance(filelist, list), f"filelist must be a list: {filelist}"
    for each in filelist:
        assert_path(each)
    assert isinstance(sep, str), f"sep should be a string: {sep}"
    assert isinstance(prefix, str), f"prefix should be a string: {sep}"
    assert isinstance(chunk_size, int), f"chunk size should be an int: {chunk_size}"
    assert chunk_size > 0, f"chunk_size should not be zero"

    # MAINF UNCTION
    # init set that will hold empty column indices
    na_cols = set()
    # counter because first iteration is different
    counter = 0
    for file in filelist:
        # init search of columns to drop if null across all chunks
        print(f"Searching {file} for empty columns...")

        with pd.read_csv(file, header=None, chunksize=chunk_size, sep=sep) as reader:
            for chunk in reader:
                null_cols = chunk.columns[chunk.isna().all()]
                # update the set with the null columns (don't take intersect yet)
                if counter < 1:
                    na_cols.update(null_cols)
                    counter += 1
                # appear in na_cols only if that col is empty across all csvs
                else:
                    na_cols = na_cols.intersection(null_cols)
                    counter += 1

    # sanity check
    print(f"Num columns to drop: {len(na_cols)} of {len(chunk.columns)}")
    print(f"Dropping columns: {na_cols}")

    # now go through the data file(s) again to drop
    for file in filelist:
        # preparing output filename
        folder, basename = os.path.split(file)
        dest_datafile = os.path.join(folder, f"{prefix}_{basename}")

        # truncate
        pd.DataFrame().to_csv(
            dest_datafile, mode="w", header=False, index=False, sep=sep
        )

        with pd.read_csv(file, header=None, chunksize=chunk_size, sep=sep) as reader:
            for chunk in reader:
                # dropping thos columns
                chunk = chunk.drop(na_cols, axis=1)
                # dropping dupes
                chunk = chunk.drop_duplicates()
                chunk.to_csv(
                    dest_datafile, mode="a", header=False, index=False, sep=sep
                )
        # sanity check
        print(f"New data file with non-empty columns saved to: {dest_datafile}")

    # drop those cols from the header file
    # finding matching heade r file
    folder, basename = os.path.split(filelist[0])
    search_header = re.sub("-data*\d*", "-header", basename)
    matching_header = filter_filepaths(
        folder, identifiers=[search_header], exclude=[prefix]
    )[0]
    print(f"Matching header file: {matching_header}")
    # preparing output filename
    dest_headfile = os.path.join(
        folder, f"{prefix}_{os.path.basename(matching_header)}"
    )

    head_df = pd.read_csv(matching_header, header=None, sep=sep)
    head_df = head_df.drop(na_cols, axis=1)
    new_head = pd.DataFrame(columns=head_df.loc[0, :])
    new_head.to_csv(dest_headfile, mode="w", header=True, index=False, sep=sep)
    # sanity check
    print(f"New header file with non-empty columns saved to: {dest_headfile}")
