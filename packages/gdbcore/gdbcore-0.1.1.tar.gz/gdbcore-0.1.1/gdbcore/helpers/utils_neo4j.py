import glob
import os
import re

import pandas as pd
from neo4j import GraphDatabase
from neo4j import __version__ as neo4j_version

from gdbcore.helpers.utils import filter_filepaths


class Neo4jConnection:
    """
    - Connects to Neo4j Graph Database
    - src: https://towardsdatascience.com/neo4j-cypher-python-7a919a372be7
    - Requirements: Neo4j desktop app and running database instance

    EXAMPLE
    -----
    >>> connection = Neo4jConnection(
        user=neo4j,
        pwd=neo4j,
        uri='bolt:localhost:7687')
    >>> connection.neo4j_version
    '5.14.1'
    """

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        self.neo4j_version = neo4j_version

        try:
            self.__driver = GraphDatabase.driver(
                self.__uri,
                auth=(self.__user, self.__pwd),
            )
        except Exception as e:
            print("Failed to create the driver:", e)

    # METHODS

    # Helper hidden methods
    def __get_dirs(self) -> dict:
        """
        Uses Neo4jConnection.query() to get database directories/paths

        RETURNS
        -----
        - A dictionary of keys=config parameter names and values=values
        """

        the_query = """
            CALL dbms.listConfig() YIELD name, value
            WHERE name CONTAINS 'dbms.directories'
            RETURN name, value
            """
        # querying the database
        db_dirs = self.query(query=the_query)

        return dict(db_dirs)

    # Public methods
    def abs_import_path(self) -> str:
        """
        Gets the absolute path to the import folder corresponding to
        this graph database object.

        RETURNS
        -----
        - full_import_path (str): absolute path to import folder
        """
        # get dictionary of neo4j dbms config names:values
        paths = self.__get_dirs()
        # getting main neo4j dbms filepath
        main = paths["dbms.directories.neo4j_home"]
        # getting import subdir name
        import_dir = paths["dbms.directories.import"]
        # getting absolute path
        full_import_path = os.path.abspath(os.path.join(main, import_dir))

        # postconditional tests
        assert os.path.exists(
            full_import_path
        ), f"error with neo4j import directory: {full_import_path} does not exist."

        return full_import_path

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query: str, params: dict = {}, db: str | None = None):
        """
        Executes cypher queries.

        INPUTS
        -----
        query (str): the cypher query
        params (dict): if using parameters in the cypher query,
            the key should be the variable name and
            the value pair should be the value
        db (str or None): the name of the database you want to query

        RETURNS
        -----
        - response (list): is the query result

        EXAMPLES
        -----
        1)
        disease_count = connection.query(
            query='''
            MATCH (n:AnalyticalSample)
            RETURN COUNT(*) as sample_count, n.group as disease;
            ''',
            db=ckgdump
        )

        2) with_params_example = connection.query(
            query='''
            MATCH (n:$some_label)
            RETURN COUNT(*) as sample_count, n.group as disease;
            ''',
            params={'some_label': 'AnalyticalSample'},
            db=ckgdump
        )
        """

        # PRECONDITIONALS
        assert self.__driver is not None, "Driver not initialized!"
        if db is not None:
            assert isinstance(db, str), "database name must be a string"
        assert isinstance(params, dict), "params must be a dict"

        session = None
        response = None

        try:
            session = (
                self.__driver.session(database=db)
                if db is not None
                else self.__driver.session()
            )

            # adding params option to use in 'run' method
            if len(params) == 0:
                response = list(session.run(query))
            else:
                response = list(session.run(query, parameters=params))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()

        return response

    def get_import_dir_contents(self, local_prefix: bool = True):
        """
        getting filecontents with 'file:///' prefix
        """

        files = glob.glob(f"{self.abs_import_path()}/**")

        if local_prefix:
            return [x.replace(self.abs_import_path(), "file://") for x in files]
        else:
            return files

    def to_local_prefix(self, fnames: list):
        return [x.replace(self.abs_import_path(), "file://") for x in fnames]


def neo_query2df(query_output: list) -> pd.DataFrame:
    """
    creating a function to take query output and put in df

    Takes Neo4jConnector.query() output,
    which is a list of Neo4j records (dicts)
    and returns a pandas dataframe (df) where each record becomes a df row

    PARAMETERS
    -----
    db_connection = Neo4jConnection(uri, user, pwd)
    query_result = db_connection.query("MATCH (n) RETURN count(*) AS num_nodes"
    neo_query2df(query_result)

    OUTPUT
    -----
    pd.DataFrame
    wip

    """

    assert len(query_output) > 0, "the query output (list) is empty"

    return pd.DataFrame.from_dict([x.data() for x in query_output])


def generate_neo4j_bulk_import_command(
    db_name: str,
    nodes: dict | None = None,
    edges: dict | None = None,
    sep="|",
    quote='"',
    array_sep=",",
):
    """
    - NOTE: for this bulk import, the files don't have to exist in the import folder
    - for neo4j 4
    - this is only for an initial import!
    "The neo4j-admin import is a command for loading large amounts of data from CSV files into an unused non-existing database.
    mporting data from CSV files with neo4j-admin import can only be done once into an unused database, it is used for initial graph population only."
    """
    # PRECONDITIONS

    # MAIN FUNCTION
    # init command
    command = ""
    calling = "bin/neo4j-admin import"
    db_details = f"--database={db_name} --force=true"
    sep_options = (
        f"--delimiter='{sep}' --quote='{quote}' --array-delimiter='{array_sep}'"
    )
    command += f"{calling} {db_details} {sep_options}"

    if nodes is not None:
        for file in nodes["data_files"]:
            # get node properties
            # finding matching header file
            search_header = re.sub("-data\d*", "-header", os.path.basename(file))
            matching_header = filter_filepaths(
                nodes["header_files"], identifiers=[search_header]
            )

            # if none or more than one header file stop
            assert (
                len(matching_header) == 1
            ), f"should only be one header file: {matching_header}"

            command += f' --nodes="{matching_header[0]},{file}"'

    if edges is not None:
        for file in edges["data_files"]:
            # get node properties
            # finding matching header file
            search_header = re.sub("-data\d*", "-header", os.path.basename(file))
            matching_header = filter_filepaths(
                edges["header_files"], identifiers=[search_header]
            )

            # if none or more than one header file stop
            assert (
                len(matching_header) == 1
            ), f"should only be one header file: {matching_header}"

            command += f' --relationships="{matching_header[0]},{file}"'

    return command
