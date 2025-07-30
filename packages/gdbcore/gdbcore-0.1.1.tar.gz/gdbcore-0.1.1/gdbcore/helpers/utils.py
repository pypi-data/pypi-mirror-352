# these functions are pretty general (file that can be reused across projects)
import argparse
import csv
import glob
import logging
import os
import re
import shutil
import subprocess
import sys
import warnings
from datetime import datetime
from urllib.parse import urlparse, urlunsplit
import yaml


## CHECKS
def assert_path(filepath: str):
    """
    Checks that the given filepath is a string and that it exists.

    :param str filepath: The filepath or folder path to check.
    :raises TypeError: If the filepath is not a string.
    :raises FileNotFoundError: If the filepath does not exist.
    """

    if not isinstance(filepath, str):
        raise TypeError(f"filepath must be a string: {type(filepath)}")
    if not os.path.exists(os.path.abspath(filepath)):
        raise FileNotFoundError(f"The specified path does not exist: {filepath}")


def create_folder(directory_path: str, is_nested: bool = False) -> bool:
    """
    alternative to assert_path to create folder if it doesn't exist
    :param directory_path: The path of the directory to create.
    :type directory_path: str
    :param is_nested: A flag indicating whether to create nested directories (True uses os.makedirs, False uses os.mkdir).
    :type is_nested: bool
    :returns: True if the folder was created or False if it already existed.
    :rtype: bool
    :raises OSError: If there is an error creating the directory.
    """
    # PRECONDITION CHECK
    if not isinstance(directory_path, str):
        raise TypeError(f"filepath must be a string: {type(directory_path)}")
    abs_path = os.path.abspath(directory_path)

    # make sure it is a folder not a file
    if os.path.isfile(abs_path):
        raise ValueError(
            f"directory_path is an existing file when it should be a folder/foldername: {abs_path}"
        )
    # if folder already exists
    elif os.path.isdir(abs_path):
        return False
    # create the folder(s)
    else:
        try:
            if is_nested:
                # Create the directory and any necessary parent directories
                os.makedirs(directory_path, exist_ok=True)
                return True
            else:
                # Create only the final directory (not nested)
                os.mkdir(directory_path)
                return True
        except OSError as e:
            raise OSError(f"Error creating directory '{directory_path}': {e}")


def assert_nonempty_keys(dictionary: dict):
    """
    - Checks that the keys are not empty strings
    - Can they be numbers? I guess

    PARAMS
    -----
    - dictionary (dict): a dictionary e.g. config file
    """

    # PRECONDITIONS
    assert isinstance(dictionary, dict), "dictionary must be a dict"

    # MAIN FUNCTION
    for key in dictionary:
        if type(key) is str:
            assert key, f'There is an empty key (e.g., ""): {key, dictionary.keys()}'
            assert (
                key.strip()
            ), f'There is a blank key (e.g., space, " "): {key, dictionary.keys()}'


def assert_nonempty_vals(dictionary: dict):
    """
    - Checks that the dict values are not empty strings

    PARAMS
    -----
    - dictionary (dict): a dictionary e.g. config file
    """

    # PRECONDITIONS
    assert isinstance(dictionary, dict), "dictionary must be a dict"

    # MAIN FUNCTION
    for v in dictionary.items():
        if type(v) is str:
            assert v, f'There is an empty key (e.g., ""): {v, dictionary.items()}'
            assert (
                v.strip()
            ), f'There is a blank key (e.g., space, " "): {v, dictionary.items()}'


def warn_folder(
    folderpath: str,
    warning_message: str = "Warning: There are existing files in the given folderpath.",
):
    """
    Checks if the folder is empty. If not empty, raises a warning.

    :param folderpath: Path to the folder.
    :type folderpath: str
    :param warning_message: Warning message to display if the folder is not empty, defaults to "Warning: There are existing files in the given folderpath."
    :type warning_message: str, optional

    :raises FileNotFoundError: If the specified path does not exist.
    :raises AssertionError: If the warning message is not a string.

    :return: Warning message if files exist in the folder.
    :rtype: str

    EXAMPLES
    -----
    1)
    >>> warn_folder('/Users/this/that/empty_folder')

    2)
    >>> warn_folder('/Users/this/that/non_empty_folder')
    Warning: There are existing files in the given folderpath.
    """

    # PRECONDITIONS
    assert_path(folderpath)
    assert isinstance(
        warning_message, str
    ), f"warning message must be string: {warning_message}"

    if len(glob.glob(os.path.join(folderpath, "*"))) > 0:
        warnings.warn(warning_message, UserWarning)

        return warning_message


def normalize_url(host: str, port: int, scheme: str = "http") -> str:
    """
    Normalize the given URL. Ensure the URL starts with 'http://'

    This function takes a URL and normalizes it by ensuring it has a scheme,
    converting it to lowercase, and removing any trailing slashes.

    :param host: The host to be normalized.
    :type host: str
    :param port: The port
    :type port: int
    :param scheme: the scheme
    :type scheme: str
    :return: The normalized URL.
    :rtype: str

    """
    ## PRECONDITIONS
    if not isinstance(host, str):
        raise TypeError(f"host should be a str e.g., 'localhost': {type(host)}")
    if not isinstance(port, int):
        raise TypeError(f"port must be int e.g., '7474': {type(port)}")
    if not isinstance(scheme, str):
        raise TypeError(f"scheme must be str: {type(scheme)}")

    ## MAIN FUNCTION
    if not urlparse(host).netloc:
        host = urlunsplit([scheme, host, "", "", ""])

    # Remove any trailing slashes
    url = host.rstrip("/")

    # Add the port
    url = f"{url}:{str(port)}"

    ## POSTCOND CHECKS
    if not urlparse(url).netloc:
        raise TypeError(f"Unable to normalize url: {url}")

    return url


# FUNCTIONS FOR CONFIG
def config_loader(filepath: str) -> dict:
    """
    Loads in yaml config file as dict

    PARAMETERS
    -----
    - filepath (str): path to the config file

    RETURNS
    -----
    - contents (dict): configuration parameters as a dictionary

    EXAMPLE
    -----
    >>> config_dict = config_loader('config/config.yaml')

    """

    # PRECONDITIONS
    assert_path(filepath)

    # MAIN FUNCTION
    with open(filepath, "r") as f:
        contents = yaml.safe_load(f)

    # POSTCONDITIONS
    assert isinstance(contents, dict), "content not returned as a dict"

    return contents


def get_args(prog_name: str, others: dict = {}):
    """
    Initiates argparse.ArugmentParser() and adds common arguments.

    :param prog_name: The name of the program.
    :type prog_name: str

    :returns:
    :rtype:
    """
    ### PRECONDITIONS
    if not isinstance(prog_name, str):
        raise TypeError(f"prog_name should be a string: {type(prog_name)}")
    if not isinstance(others, dict):
        raise TypeError(f"other kwargs must be a dict: {type(others)}")
    ## MAIN FUNCTION
    # init
    parser = argparse.ArgumentParser(prog=prog_name, **others)
    # config file path
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        default="demo/config.yaml",
        help="provide path to config yaml file",
    )
    args = parser.parse_args()
    return args


## FOR LOGGING
def get_basename(fname: None | str = None) -> str:
    """
    - For a given filename, returns basename WITHOUT file extension
    - If no fname given (i.e., None) then return basename that the function is called in

    PARAMS
    -----
    - fname (None or str): the filename to get basename of, or None

    OUTPUTS
    -----
    - basename of given filepath or the current file the function is executed

    EXAMPLES
    -----
    1)
    >>> get_basename()
    utils

    2)
    >>> get_basename('this/is-a-filepath.csv')
    is-a-filepath
    """
    if fname is not None:
        # PRECONDITION
        assert_path(fname)
        # MAIN FUNCTIONS
        return os.path.splitext(os.path.basename(fname))[0]
    else:
        return os.path.splitext(os.path.basename(sys.argv[0]))[0]


def get_time(incl_time: bool = True, incl_timezone: bool = True) -> str:
    """
    Gets current date, time (optional) and timezone (optional) for file naming

    PARAMETERS
    -----
    - incl_time (bool): whether to include timestamp in the string
    - incl_timezone (bool): whether to include the timezone in the string

    RETURNS
    -----
    - fname (str): includes date, timestamp and/or timezone
        connected by '_' in one string e.g. yyyyMMdd_hhmm_timezone

    EXAMPLES
    -----
    1)
    >>> get_time()
    '20231019_101758_CEST'

    2)
    >>> get_time(incl_time=False)
    '20231019_CEST'

    """

    # PRECONDITIONALS
    if not isinstance(incl_time, bool):
        raise TypeError("incl_time must be True or False")
    if not isinstance(incl_timezone, bool):
        raise TypeError("incl_timezone must be True or False")

    # MAIN FUNCTION
    # getting current time and timezone
    the_time = datetime.now()
    timezone = datetime.now().astimezone().tzname()
    # convert date parts to string
    y = str(the_time.year)
    M = str(the_time.month)
    d = str(the_time.day)
    h = str(the_time.hour)
    m = str(the_time.minute)
    s = str(the_time.second)
    # putting date parts into one string
    if incl_time and incl_timezone:
        fname = "_".join([y + M + d, h + m + s, timezone])
    elif incl_time:
        fname = "_".join([y + M + d, h + m + s])
    elif incl_timezone:
        fname = "_".join([y + M + d, timezone])
    else:
        fname = y + M + d

    # POSTCONDITIONALS
    parts = fname.split("_")
    if incl_time and incl_timezone:
        assert len(parts) == 3, f"time and/or timezone inclusion issue: {fname}"
    elif incl_time or incl_timezone:
        assert len(parts) == 2, f"time/timezone inclusion issue: {fname}"
    else:
        assert len(parts) == 1, f"time/timezone inclusion issue: {fname}"

    return fname


def generate_log_filename(folder: str = "logs", suffix: str = "") -> str:
    """
    Creates log file name and path

    PARAMETERS
    -----
    folder (str): name of the folder to put the log file in
    suffix (str): anything else you want to add to the log file name

    RETURNS
    -----
    log_filepath (str): the file path to the log file
    """
    # PRECONDITIONS
    create_folder(folder)

    # MAIN FUNCTION
    log_filename = get_time(incl_timezone=False) + "_" + suffix + ".log"
    log_filepath = os.path.join(folder, log_filename)

    return log_filepath


def init_log(filename: str, display: bool = False, logger_id: str | None = None):
    """
    - Custom python logger configuration (basicConfig())
        with two handlers (for stdout and for file)
    - from: https://stackoverflow.com/a/44760039
    - Keeps a log record file of the python application, with option to
        display in stdout

    PARAMETERS
    -----
    - filename (str): filepath to log record file
    - display (bool): whether to print the logs to whatever standard output
    - logger_id (str): an optional identifier for yourself,
        if None then defaults to 'root'

    RETURNS
    -----
    - logger object

    EXAMPLE
    -----
    >>> logger = init_log('logs/tmp.log', display=True)
    >>> logger.info('Loading things')
    [2023-10-20 10:38:03,074] root: INFO - Loading things
    """
    # PRECONDITIONS
    if not isinstance(filename, str):
        raise TypeError(f"filename must be a string: {filename}")
    if not (isinstance(logger_id, str) or logger_id is None):
        raise TypeError("logger_id must be a string or None")

    # MAIN FUNCTION
    # init handlers
    file_handler = logging.FileHandler(filename=filename)
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    if display:
        handlers = [file_handler, stdout_handler]
    else:
        handlers = [file_handler]

    # logger configuration
    logging.basicConfig(
        # level=logging.DEBUG,
        format="[%(asctime)s] %(name)s: %(levelname)s - %(message)s",
        handlers=handlers,
    )
    logging.getLogger("matplotlib.font_manager").disabled = True

    # instantiate the logger
    logger = logging.getLogger(logger_id)
    logger.setLevel(logging.DEBUG)

    return logger


def get_logger():
    """
    Putting at all together to init the log file.
    """
    # get log suffix, which will be the current script's base file name
    log_suffix = get_basename()
    # generate log file name
    log_file = generate_log_filename(suffix=log_suffix)
    # init logger
    logger = init_log(log_file, display=True)
    # log it
    logger.info(f"Path to log file: {log_file}")

    return logger


# other


def find_matches(
    filepath: str, sub: tuple = ("-data\d*", "-header"), area: str | list | None = None
):
    """
    Search `area` for files matching the given `filepath` name with replaced substrings specified in `sub`

    PARAMS
    -----
    - filepath (str): path to an existing file
    - sub (tuple): substring to replace in the filepath (<pattern>, <replacement>)
        - if no sub then give a tuple with 2 empty strings i.e., ('', '')
    - area (NoneType or list or str):
        - if None then search in the same location that filepath is located
        - if list of files then search for matches within this list
        - if string should be a folderpath and will search for matches within this folder

    OUTPUTS
    -----
    - matches (list): list with matching paths
    """

    # PRECONDITIONS
    assert_path(filepath)
    assert isinstance(
        sub, tuple
    ), f"sub must be a tuple with 2 items (search, replace): {sub}"
    assert len(sub) == 2, f"sub must be a tuple with 2 items (search, replace): {sub}"
    for term in sub:
        assert isinstance(
            term, str
        ), f"items in sub tuple must be strings (can be empty stirngs): {term}"
    # check search area
    if area is None:
        # then search the folder that data_file is in
        area = os.path.split(filepath)[0]
    elif isinstance(area, str):
        assert_path(area)
        if not os.path.isdir(area):
            raise TypeError(f"area {area} is not a folder")
    elif isinstance(area, list):
        for file in area:
            assert_path(file)
    else:
        raise ValueError(
            f"area must be a folderpath as a str, or a list of files: {area}"
        )

    # MAIN FUNCTION
    search_sub = re.sub(sub[0], sub[1], get_basename(filepath))

    matches = filter_filepaths(area, identifiers=[search_sub])

    return matches


def copy_recursively(src:str, dest:str, overwrite:bool=False):
    """
    Recursively copies files and directories from `src` to `dest`.

    :param src: Source path (file or directory).
    :param dest: Destination path (file or directory).
    :param overwrite: If True, overwrite existing files. Default is False.

    Example:
    >>> copy_recursively('here', 'there', overwrite=True)
    """
    # PRECONDITIONS
    assert_path(src)
    create_folder(dest, str)

    # MAIN FUNCTION
    abs_src = os.path.abspath(src)
    abs_dest = os.path.abspath(dest)

    # If a single file to copy
    if os.path.isfile(abs_src):
        try:
            # Get file extension to check if it exists
            _, fext = os.path.splitext(abs_dest)
            # Subdirectories
            subdirs = os.path.split(abs_dest)[0]

            # If destination file already exists
            if os.path.isfile(abs_dest):
                if overwrite:
                    print(f"Overwriting file:\n\t{abs_dest}")
                    shutil.copy2(abs_src, abs_dest)
                else:
                    print(f"Skipping (already exists):\n\t{abs_dest}")
            # If destination is an existing directory, copy file with the same name
            elif os.path.isdir(abs_dest):
                print(f"{abs_dest} is a directory")
                new_dest = os.path.join(abs_dest, os.path.basename(abs_src))
                if os.path.isfile(new_dest) and not overwrite:
                    print(f"Skipping (already exists):\n\t{new_dest}")
                else:
                    print(f"Copying file to:\n\t{new_dest}")
                    shutil.copy2(abs_src, new_dest)
        except Exception as e:
            print(f"Error copying file: {e}")

    # If a directory to copy
    elif os.path.isdir(abs_src):
        try:
            # Ensure destination directory exists
            os.makedirs(abs_dest, exist_ok=True)
            for root, dirs, files in os.walk(abs_src):
                # Create subdirectories
                for dir_name in dirs:
                    src_dir = os.path.join(root, dir_name)
                    dest_dir = os.path.join(abs_dest, os.path.relpath(src_dir, abs_src))
                    os.makedirs(dest_dir, exist_ok=True)

                # Copy files
                for file_name in files:
                    src_file = os.path.join(root, file_name)
                    dest_file = os.path.join(abs_dest, os.path.relpath(src_file, abs_src))
                    if os.path.isfile(dest_file) and not overwrite:
                        print(f"Skipping (already exists):\n\t{dest_file}")
                    else:
                        print(f"Copying file to:\n\t{dest_file}")
                        shutil.copy2(src_file, dest_file)
        except Exception as e:
            print(f"Error copying directory: {e}")
    else:
        raise ValueError(f"Source path does not exist or is invalid: {src}")


def filter_filepaths(
    fpath: str | list, identifiers: list = [""], exclude: None | list = None
) -> list:
    """
    Isolating files to iterate through. Can provide multiple identifiers.
    if list given, then filters list.
    if str/path given, then acquires list first.
    """

    # PRECONDITIONALS
    if not isinstance(identifiers, list):
        raise TypeError("exclude must be None or a list of strngs")
    for id in identifiers:
        if not isinstance(id, str):
            raise TypeError(f"must all be strings: {id} not a string")

    if exclude is not None:
        if not isinstance(exclude, list):
            raise TypeError("exclude must be None or a list of strngs")
        for ex in exclude:
            if not isinstance(ex, str):
                raise TypeError(f"must all be strings: {ex} not a string")

    # MAIN FUNCTION

    # if path (str) given then get a list of files first
    if type(fpath) is str:
        assert_path(fpath)
        # get list of containing files
        filepaths = glob.glob(f"{fpath}/**", recursive=True)
    # if a list of filenames then continue
    elif type(fpath) is list:
        filepaths = fpath
    else:
        raise TypeError(f"fpath must be a string or list: {type(fpath)}")

    # filtering for files that have those identifiers
    in_filtered = [
        file
        for file in filepaths
        if all([id in os.path.basename(file) for id in identifiers])
    ]

    if exclude is None:
        return in_filtered
    else:
        # filter out the files that match in the exclusion list
        ex_filtered = [
            file
            for file in in_filtered
            if all([ex not in os.path.basename(file) for ex in exclude])
        ]

        return ex_filtered


def group_files(
    source_folder: str | list,
    sub: tuple = ("-datab*\d*.csv", ""),
    include_files_with: list = [""],
    exclude_files_with: None | list = None,
) -> dict:
    """
    - In a given folder, or list of files, groups the files based on naming
    - Main puropse is to group multicsvs in a list

    PARAMS
    -----
    - source_folder (str or list): path to folder with the datafiles or list of datafiles
    - sub (tuple): substring to replace in the filepath (<pattern>, <replacement>)
        - if no sub then give a tuple with 2 empty strings i.e., ('', '')
    - exclude_files_with (None or list): a list of strings for use in filter_filepaths(exclude=)
    - include_files_with (list): a list of strings for use in filter_filepaths(identifiers=)

    OUTPUTS
    -----
    - grouped_files (dict): a dictionary of lists where key is the group identifier, and
        list contains files that matched


    """
    # PRECONDITIONS
    if isinstance(source_folder, str):
        assert_path(source_folder)
    else:
        if not isinstance(source_folder, list):
            raise TypeError(
                f"source_folder must be a folderpath or a list of filepaths: {source_folder}"
            )
        for file in source_folder:
            assert_path(file)
    if not isinstance(sub, tuple):
        raise TypeError(f"sub must be a tuple with 2 items (search, replace): {sub}")
    if not len(sub) == 2:
        raise ValueError(f"sub must be a tuple with 2 items (search, replace): {sub}")
    if exclude_files_with is not None:
        if not isinstance(exclude_files_with, list):
            raise TypeError(
                f"exclude_files_with must be a list of strings: {exclude_files_with}"
            )
        for ex in exclude_files_with:
            if not isinstance(ex, str):
                raise TypeError(f"exclude_files_with must be a list of strings: {ex}")
    if not isinstance(include_files_with, list):
        raise TypeError(
            f"include_files_with must be a list of strings: {include_files_with}"
        )
    for i in include_files_with:
        if not isinstance(i, str):
            raise TypeError(f"include_files_with must be a list of strings: {i}")

    # MAIN FUNCTION
    # init dict
    grouped_files = {}
    # getting all data files
    result = filter_filepaths(
        source_folder, identifiers=include_files_with, exclude=exclude_files_with
    )
    # isolating unique main file names
    files_only = [f for f in result if os.path.isfile(f)]
    file_groups = set([re.sub(sub[0], sub[1], fname) for fname in files_only])
    # generate grouped lists
    for file in file_groups:
        grouped_files[file] = [f for f in files_only if file in f]

    return grouped_files


def get_header(
    filepath: str, row: int = 0, sep: str = "|", quotechar: str = '"'
) -> list:
    """
    Gets the header row from a csv file and returns as a list.

    PARAMS
    -----
    - filepath (str): path to file, should be a csv file
    - row (int): the index of the row that contains the header
    - sep (str): the delimiter of the csv file
    - quotechar (str): quote character

    OUTPUTS
    -----
    - header_list (list): the header as a list with each column as an item

    EXAMPLES
    -----
    """
    # PRECONDITIONS
    assert_path(filepath)
    assert isinstance(row, int), "row number should be an integer"
    assert isinstance(sep, str), "sep should be given as a string"
    assert isinstance(quotechar, str), "quotechar should be given as a string"

    # MAIN FUNCTION
    if row > 0:
        # read in header from csv (this takes a long time if its a big file ..)
        with open(filepath) as fp:
            reader = csv.reader(fp, delimiter=sep, quotechar=quotechar)
            all_rows = list(reader)
            assert row < len(all_rows), "given row index outside of csv indices"
            header_list = all_rows[row]
    else:
        # read in first row from csv only (faster)
        with open(filepath) as fp:
            reader = csv.reader(fp, delimiter=sep, quotechar=quotechar)
            header_list = next(reader)

    # POSTCONDITIONALS
    assert len(header_list) > 0, "Empty header list!"

    return header_list


def pipe(input, functions: list = []):
    """
    - Pipes output of one function into another like '|' in linux
    - https://stackoverflow.com/questions/28252585/functional-pipes-in-python-like-from-rs-magrittr
    - Limitation:
        - All functions must only expect one argument
        - Defaults will have to be used for all other arguments

    PARAMS
    -----
    - input (Any): whatever input the first function is expecting
    - functions (list): a list of functions IN ORDER OF EXECUTION
        do not include () at end of functions

    OUTPUTS
    -----
    - Any or None (whatever the expected output is from the final function in the list)

    """
    # PRECONDITIONALS
    if not isinstance(functions, list):
        raise TypeError("functions should be in a list")
    for f in functions:
        if not callable(f):
            raise TypeError(f"{f} is not a function")

    # MAIN FUNCTION
    for f in functions:
        input = f(input)
    return input


def get_line_count(filepath: str) -> int:
    """
    Retreives the line count of a file
    https://stackoverflow.com/questions/64744161/best-way-to-find-out-number-of-rows-in-csv-without-loading-the-full-thing
    """
    # PRECONDITIONS
    assert_path(filepath)
    abspath = os.path.abspath(filepath)
    if not os.path.isfile(abspath):
        raise TypeError(f"{abspath} is not a file.")

    # MAIN FUNCTION
    query_result = subprocess.check_output(f"wc -l {abspath}", shell=True)
    try:
        count_lines = int(query_result.split()[0])
    except ValueError:
        raise

    # POSTCONDITION
    if not isinstance(count_lines, int):
        raise TypeError("line count result not returned as an int")

    return count_lines
