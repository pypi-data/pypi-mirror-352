import csv
import os
import re

from gdbcore.helpers.utils import filter_filepaths, find_matches, get_header


def cypher_dtypes_mapping():
    """
    - a default dictionary that maps the python datatype to cypher
    """
    # init
    cypher_datatypes = {
        "str": "STRING",
        "list": "STRING[]",  # deal with all lists as list of strings for now
        "int": "INT",
        "float": "FLOAT",
        "bool": "BOOLEAN",
    }

    return cypher_datatypes


def cypher_camelcase(attribute_name: str, lower_first: bool = True) -> str:
    """
    - re-formatting node attribute name so that it is camelCase (first word lowercase)
    - assumes that words are separated by '-', '_', or ' '

    INPUT:
    ------
    - attribute_name (str): the name of the attribute
    - lower_first (bool): if true the first word will not start with an uppercase letter

    OUTPUT:
    ------
    - string with attribute name formatted to cypher recommendations

    EXAMPLES:
    -----
    1)
    cypher_camelcase(attribute_name='This-is an ! Example ', lower_first=True)
    >>> 'thisIsAnExample'

    2)
    cypher_camelcase(attribute_name='another_example', lower_first=False)
    >>> 'AnotherExample'
    """

    # PRECONDITIONALS
    assert isinstance(attribute_name, str), "name must be a string"

    # MAIN FUNCTION

    # make lower case and replace - and _ with spaces
    add_spaces = attribute_name.lower().replace("-", " ").replace("_", " ")
    # upper first letter of each word
    upper_words = add_spaces.title()
    # finally, remove special characters
    upper_name = re.sub(r"\W+", "", upper_words)

    # POSTCONDITIONAL CHECKS
    assert len(re.findall(r"\W+", upper_name)) == 0, "special characters remaining"

    # if lower_first is set to true then make camelCase
    if lower_first == True:
        lower_name = upper_name[0].lower() + upper_name[1:]
        assert lower_name[0].islower(), "first character not made into lowercase"

        return lower_name

    else:
        return upper_name


def cypher_upper(relationship: str) -> str:
    """
    - takes a relationship type and formats as UPPER_CASE as per cypher formating
    """
    # PRECONDITIONALS
    assert isinstance(relationship, str), "name must be a string"

    # MAIN FUNCTION
    # make upper case and replace - and spaces with _
    uppercase = relationship.upper().replace("-", "_").replace(" ", "_")
    # finally, remove special characters
    upper_rel = re.sub(r"\W+", "", uppercase)

    # POSTCONDITIONAL CHECKS
    assert len(re.findall(r"\W+", upper_rel)) == 0, "special characters remaining"

    return upper_rel


def get_cypher_named_columns(attributes: dict) -> dict:
    """
    - Takes a dictionary with column_name:datatype and creates a mapping of
        original_name (key) to cypher column name (value)
    - original name -> Cypher column naming looks like:
        e.g. Birth Year -> birthYear:INT
        e.g. Foods -> foods:STRING[]
        e.g. species -> species:STRING

    PARAMS
    -----
    - attributes (dict): key:value pair is equal to node-attribute-name:python datatype
        e.g. output from utils_obo.get_node_attributes_dtypes()

    OUTPUTS
    -----
    - col_names (dict): key_value pair is original_name:cypher_naming
    """

    # PRECONDITIONS

    # dictionary input check
    assert isinstance(attributes, dict), "attributes must be a dictionary"
    assert len(attributes) != 0, "empty dictionary"
    # check that keys and values in dict are strings
    for k, v in attributes.items():
        assert isinstance(k, str), "key in attributes dictionary must be a string"
        assert isinstance(v, str), "value in attributes dictionary must be a string"

    # for mapping to cypher equivalent
    cypher_datatypes = cypher_dtypes_mapping()
    # check that the datatypes exist in 'cypher_datatypes'
    unique_dtypes = set(attributes.values())
    assert all(
        [dtype in cypher_datatypes.keys() for dtype in unique_dtypes]
    ), f"{unique_dtypes} datatype(s) is not in cypher_dtypes_mapping(): {cypher_datatypes.keys()}"

    # MAIN FUNCTION
    # instantiate column names list
    col_names = {}

    for attr_name, attr_dtype in attributes.items():
        # re-formatting node attribute name so that it is camelCase (first word lowercase)
        # also, gets cypher dtype mapping
        col_names[attr_name] = (
            f"{cypher_camelcase(attr_name)}:{cypher_datatypes[attr_dtype]}"
        )

    return col_names


def cypher_unformat_dtypes(columns: list) -> list:
    """
    - Removes cypher-style formating from column names
    - Specifically removes datatypes from the end of the column name
    - leaves :LABEL and :TYPE columns as is

    PARAMS
    -----
    - columns (list): header list, a list of column names
        e.g. the output from utils.get_header()

    OUTPUTS
    -----
    - new_columns (list): column list but without cypher datatypes

    """
    # PRECONDITIONS
    assert isinstance(columns, list), "columns should be a list"
    assert len(columns) > 0, "columns list empty!"
    for col in columns:
        assert isinstance(col, str), "each col name should be a str"

    # MAIN FUNCTION
    # leave the column name as is if in this list
    ids_keep = [":LABEL", ":TYPE", ":START_ID", ":END_ID"]
    # add lowercase vers
    ids_keep += [id.lower() for id in ids_keep]

    new_columns = [x.split(":")[0] if (x not in ids_keep) else x for x in columns]

    # POSTCONDITIONS
    assert (
        len(columns) == len(new_columns)
    ), f"different length lists: new length {len(new_columns)} should be original {len(columns)}"

    return new_columns


def cypher_get_label_index(header_list: list) -> int:
    """
    Get the index of the column that has the labels for the node and edge header files

    PARAMS
    -----
    - header_list (list): header list, a list of column names
        e.g. the output from utils.get_header()
            or utils_cypher.cypher_unformat_dtypes()

    OUTPUTS
    -----
    - label_col_index (int): the index of the column that has the node/edge labels

    EXAMPLES

    -----

    """
    # PRECONDITIONS
    assert isinstance(header_list, list), "header_list should be a list"
    assert len(header_list) > 0, "header_list list empty!"
    for col in header_list:
        assert isinstance(col, str), "each col name should be a str"

    # MAIN FUNCTION
    # get the index of the label column
    try:
        if ":TYPE" in header_list:
            label_col_index = header_list.index(":TYPE")
        else:
            label_col_index = header_list.index(":LABEL")
    except Exception as e:
        print(f"no column with label/type: {header_list}", e)

    # POSTCONDITIONS
    assert isinstance(label_col_index, int), f"{label_col_index} is not an integer"

    return label_col_index


def cypher_get_start_id_index(header_list: list) -> int:
    """
    Get the index of the column that has the START_IDs for the edge files

    PARAMS
    -----
    - header_list (list): header list, a list of column names
        e.g. the output from utils.get_header()
            or utils_cypher.cypher_unformat_dtypes()

    OUTPUTS
    -----
    - start_col_index (int): the index of the column that has the node start_ids

    EXAMPLES

    -----

    """
    # PRECONDITIONS
    assert isinstance(header_list, list), "header_list should be a list"
    assert len(header_list) > 0, "header_list list empty!"
    for col in header_list:
        assert isinstance(col, str), "each col name should be a str"

    # MAIN FUNCTION
    # get the index of the label column
    if ":START_ID" in header_list:
        start_col_index = header_list.index(":START_ID")
    elif ":start_id" in header_list:
        start_col_index = header_list.index(":start_id")
    else:
        start_col_index = "no column with :START_ID"

    return start_col_index


def cypher_get_end_id_index(header_list: list) -> int:
    """
    Get the index of the column that has the END_IDs for the edge files

    PARAMS
    -----
    - header_list (list): header list, a list of column names
        e.g. the output from utils.get_header()
            or utils_cypher.cypher_unformat_dtypes()

    OUTPUTS
    -----
    - end_col_index (int): the index of the column that has the node end_ids

    EXAMPLES

    -----

    """
    # PRECONDITIONS
    assert isinstance(header_list, list), "header_list should be a list"
    assert len(header_list) > 0, "header_list list empty!"
    for col in header_list:
        assert isinstance(col, str), "each col name should be a str"

    # MAIN FUNCTION
    # get the index of the label column
    if ":END_ID" in header_list:
        end_col_index = header_list.index(":END_ID")
    elif ":end_id" in header_list:
        end_col_index = header_list.index(":end_id")
    else:
        end_col_index = "no column with :END_ID"

    return end_col_index


def cypher_get_label(data_file: str, label_col: int, sep="|", quotechar='"') -> str:
    """
    this only returns the first row of the data file
    so limitation/requirement here: only one label/reltype per file
    """
    # go into data file and get label
    with open(data_file) as fp:
        reader = csv.reader(fp, delimiter=sep, quotechar='"')
        label = next(reader)[label_col]

    return label


def cypher_query_load_nodes(
    header_files: list,
    data_files: list,
    num_transactions: int = 500,
    sep: str = "|",
    quotechar: str = '"',
    fill_na="Unknown",
) -> list:
    """
    - Gets lists of node loading queries to update in a db
    - Requirements:
        - the header and data files must have same naming
            except for the suffix "-header" "-data"
        - the header and data files should be in the Neo4j Database import folder
            use ` neo4j_driver.abs_import_path() ` to get path param
    """
    queries = []

    for file in data_files:
        # get node properties

        # finding matching header file
        matching_header = find_matches(filepath=file, area=header_files)

        assert (
            len(matching_header) == 1
        ), f"{file} should only have one matching header file: {matching_header}"

        matched_header_file = matching_header[0]

        # getting the properties portion of query
        node_props = cypher_query_generate_properties(
            data_file=file,
            header_file=matched_header_file,
            sep=sep,
            quotechar=quotechar,
            fill_na=fill_na,
        )

        query = f"""
        LOAD CSV FROM "{file}" AS line FIELDTERMINATOR '{sep}'
        CALL {{
            WITH line
            MERGE ({node_props})
        }} IN TRANSACTIONS OF {num_transactions} ROWS
        RETURN DISTINCT file() as path
        """

        queries.append(query)

    return queries


def cypher_query_generate_properties(
    data_file: str,
    header_file: str,
    sep: str = "|",
    quotechar: str = '"',
    fill_na="Unknown",
) -> str:
    """
    This function works for both node and edge lists
    Generating the {node_props} portion of the below cypher query

        query = f'''
        LOAD CSV FROM "{file}" AS line FIELDTERMINATOR '{sep}'
        CALL {{
            WITH line
            MERGE ({node_props})
        }} IN TRANSACTIONS OF {num_transactions} ROWS
        RETURN DISTINCT file() as path

        LOAD CSV FROM 'file:///people.csv' AS line FIELDTERMINATOR '{sep}'
        CALL {
            WITH line
            MATCH (s {{id: line[0]}})
            MATCH (e {{id: line[1]}})
            CREATE (s)-[:{REL} {{prop}: line[3]}]->(e)
        } IN TRANSACTIONS OF {num_transactions} ROWS
        RETURN DISTINCT file() as path;
        '''
    """

    # PRECONDITIONS
    assert isinstance(data_file, str), "path to data_file must be a str"
    assert os.path.exists(data_file), f"{data_file} does not exist."
    assert isinstance(header_file, str), "path to header_file must be a str"
    assert os.path.exists(header_file), f"{header_file} does not exist."
    assert isinstance(sep, str), "sep should be given as a string"
    assert isinstance(quotechar, str), "quotechar should be given as a string"
    assert fill_na is not None, "provide a value for fill_na"

    # MAIN FUNCTION

    properties = []

    # get header
    original_header = get_header(filepath=header_file, sep=sep, quotechar=quotechar)

    # remove dtype formating
    columns = cypher_unformat_dtypes(original_header)

    # get index of labels, start, end columns in node/edge header and data files
    try:
        # should always be returned as int, if not then
        label_index = cypher_get_label_index(columns)
        start_index = cypher_get_start_id_index(columns)
        end_index = cypher_get_end_id_index(columns)
        skip = [label_index, start_index, end_index]
    except Exception as e:
        print(
            f"There was an issue retrieving the column indices of :TYPE/:LABEL, :START_ID, :END_ID: {columns}",
            e,
        )

    # get label
    edge_label = cypher_get_label(
        data_file=data_file, label_col=label_index, sep=sep, quotechar=quotechar
    ).strip(":")

    # generating query portions
    for col in columns:
        # get column number/index
        line_num = columns.index(col)

        # if not label, startid or endid column proceed to treat it as a property column
        if line_num not in skip:
            # property name = column name in header
            properties.append(f'{col}: COALESCE(line[{line_num}], "{fill_na}")')

    # if the file doesn't contain additional properties/atrributes just return label w/o props
    if len(properties) > 0:
        edge_prop = f":{edge_label} {{{', '.join(properties)}}}"
        return edge_prop
    else:
        return f":{edge_label}"


def cypher_query_load_edges(
    header_files: list,
    data_files: list,
    num_transactions: int = 500,
    sep: str = "|",
    quotechar: str = '"',
    fill_na="Unknown",
) -> list:
    """
    - Gets lists of node loading queries to update in a db
    - Requirements:
        - the header and data files must have same naming
            except for the suffix "-header" "-data"
        - the header and data files should be in the Neo4j Database import folder
            use ` neo4j_driver.abs_import_path() ` to get path param

    LOAD CSV FROM 'file:///people.csv' AS line FIELDTERMINATOR '{sep}'
        CALL {
            WITH line
            MATCH (s {{id: line[0]}})
            MATCH (e {{id: line[1]}})
            CREATE (s)-[:{REL} {{prop}: line[3]}]->(e)
        } IN TRANSACTIONS OF {num_transactions} ROWS
        RETURN DISTINCT file() as path;
    """
    queries = []

    for file in data_files:
        # get node properties
        # finding matching header file
        matching_header = find_matches(filepath=file, area=header_files)

        assert (
            len(matching_header) == 1
        ), f"{file} should only have one matching header file: {matching_header}"

        matched_header_file = matching_header[0]

        edge_props = cypher_query_generate_properties(
            data_file=file,
            header_file=matched_header_file,
            sep=sep,
            quotechar=quotechar,
            fill_na=fill_na,
        )

        # also get start and end columns
        cols = get_header(matched_header_file)
        start_index = cypher_get_start_id_index(cols)
        end_index = cypher_get_end_id_index(cols)

        # check that they are indices
        assert isinstance(start_index, int), f"{start_index} in {file}:\n{cols}"
        assert isinstance(end_index, int), f"{end_index} in {file}:\n{cols}"

        query = f"""
        LOAD CSV FROM "{file}" AS line FIELDTERMINATOR '{sep}'
        CALL {{
            WITH line
            MATCH (s {{id: line[{start_index}]}})
            MATCH (e {{id: line[{end_index}]}})
            MERGE (s)-[{edge_props}]->(e)
        }} IN TRANSACTIONS OF {num_transactions} ROWS
        RETURN DISTINCT file() as path
        """

        queries.append(query)

    return queries


# APOC QUERIES
def apoc_load_csv_nodes(
    header_files: list,
    data_files: list,
    num_transactions: int = 500,
    sep: str = "|",
    quotechar: str = '"',
    fill_na="Unknown",
) -> list:
    """
    - Gets lists of node loading queries to update in a db
    - Requirements:
        - the header and data files must have same naming
            except for the suffix "-header" "-data"
        - the header and data files should be in the Neo4j Database import folder
            use ` neo4j_driver.abs_import_path() ` to get path param

    CALL apoc.periodic.iterate(
        'CALL apoc.load.csv("{file}", {{header:false, sep:"{sep}", quotechar:{quotechar}}}) YIELD list as line RETURN line'
        ,
        'MERGE ({node_props})',
    {{batchSize:{num_transactions}, iterateList:true, parallel:true}})
    """
    queries = []

    for file in data_files:
        # get node properties
        # finding matching header file
        matching_header = find_matches(filepath=file, area=header_files)

        assert (
            len(matching_header) == 1
        ), f"{file} should only have one matching header file: {matching_header}"

        matched_header_file = matching_header[0]

        # getting the properties portion of query
        node_props = cypher_query_generate_properties(
            data_file=file,
            header_file=matched_header_file,
            sep=sep,
            quotechar=quotechar,
            fill_na=fill_na,
        )

        # need to incorporate quotechar .. nextsteps
        query = f"""
        CALL apoc.periodic.iterate(
            'CALL apoc.load.csv("{file}", {{header:false, sep:"{sep}"}}) YIELD list as line RETURN line',
            'MERGE ({node_props})',
            {{batchSize:{num_transactions}, iterateList:true, parallel:true}}
        )
        """

        queries.append(query)

    return queries


def apoc_load_csv_edges(
    header_files: list,
    data_files: list,
    num_transactions: int = 500,
    sep: str = "|",
    quotechar: str = '"',
    fill_na="Unknown",
) -> list:
    """
    - Gets lists of node loading queries to update in a db
    - Requirements:
        - the header and data files must have same naming
            except for the suffix "-header" "-data"
        - the header and data files should be in the Neo4j Database import folder
            use ` neo4j_driver.abs_import_path() ` to get path param

    CALL apoc.periodic.iterate(
        'CALL apoc.load.csv("{file}", {{header:false, sep:"{sep}", quotechar:{quotechar}}}) YIELD list as line RETURN line'
        ,
        'MATCH (s {id: line[{start_index}]}) MATCH (e {id: line[{end_index}]}) MERGE (s)-[:{LABEL} {{edge_props}}]->(e)',
        {{batchSize:{num_transactions}, iterateList:true, parallel:true}}
    )
    """
    queries = []

    for file in data_files:
        # get node properties
        # finding matching header file
        matching_header = find_matches(filepath=file, area=header_files)

        assert (
            len(matching_header) == 1
        ), f"{file} should only have one matching header file: {matching_header}"

        matched_header_file = matching_header[0]

        edge_props = cypher_query_generate_properties(
            data_file=file,
            header_file=matched_header_file,
            sep=sep,
            quotechar=quotechar,
            fill_na=fill_na,
        )

        # also get start and end columns
        cols = get_header(matched_header_file)
        start_index = cypher_get_start_id_index(cols)
        end_index = cypher_get_end_id_index(cols)

        # check that they are indices
        assert isinstance(start_index, int), f"{start_index} in {file}:\n{cols}"
        assert isinstance(end_index, int), f"{end_index} in {file}:\n{cols}"

        # need to incorporate quotechar .. nextsteps
        query = f"""
        CALL apoc.periodic.iterate(
            'CALL apoc.load.csv("{file}", {{header:false, sep:"{sep}"}}) YIELD list as line RETURN line'
            ,
            'MATCH (s {{id: line[{start_index}]}}) MATCH (e {{id: line[{end_index}]}}) MERGE (s)-[{edge_props}]->(e)',
            {{batchSize:{num_transactions}, iterateList:true, parallel:false}}
        )
        """

        queries.append(query)

    return queries
