"""
- The purpose of this script is to create a Neo4j database (db) from node and edge lists 
in the form of data csv files with an associated header csv file.
- The process will be:
    - init log
    - load config parameters from config/config.yaml
    - establish neo4j python driver connection
    - move the files to *db import folder* from source folder specified in config.yaml -> db setup -> source folder
        - **to find this folder location you can use helpers.utils_neo4j.Neo4jConnection.abs_import_path()
        - if a file from source folder already exists in the db import folder then it will be skipped NOT OVERWRITTEN
    - TODO

NEO4J REQUIREMENT:
- have a running DBMS instance

FILE FORMAT REQUIREMENTS: (will include example file later and script to check/format the file sources)
- the data files and their matching header file must have the SAME
    filenaming except for the suffices of '-header.csv' and 'data.csv'
    OR '-header.csv' and 'data1.csv', 'data2.csv'
- if node files have 'node' somehwere in the base file name 
- if edge files have 'edge somewhere in the base file name
- also see here for column naming requirements: https://neo4j.com/docs/operations-manual/current/tutorial/neo4j-admin-import/
- for node lists:
    - the primary id column/property should be named 'id:ID'
    - should include a :LABEL column with label
    - only one node label type per files (e.g., if a db is going to have Gene and Protein nodes then
      they should have their own set of data+header files)
- for edge lists:
    - should hav :START_ID, :END_ID, and :TYPE columns at least
    - only one edge label type per file

this whole area is TODO
"""

# import libraries
import sys, os

# import modules
from gdbcore.helpers.utils import (
    config_loader,
    copy_recursively,
    filter_filepaths,
    get_args,
    get_logger,
)
from gdbcore.helpers.utils_neo4j import Neo4jConnection
from gdbcore.helpers.utils_cypher import cypher_query_load_nodes, cypher_query_load_edges


if __name__ == "__main__":

    ## GET ARGS
    args = get_args(
        prog_name="cypher-data-loader",
        others=dict(
            description="""
            Uses cypher queries to load nodes and rels.
            WARNING: Slower than apoc_load_queries.py.
            """
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
    # following db set up
    username = config["neo4j"]["username"]
    password = config["neo4j"]["password"]
    db_name = config["db setup"]["db_name"]
    uri = config["neo4j"]["uri"]
    sep = config["db setup"]["sep"]
    quotechar = config["db setup"]["quotechar"]
    fill_na = config["db setup"]["fill_na"]
    num_transactions = config["neo4j"]["num_transactions"]
    source_folder = config["db setup"]["source folder"]

    ## CONNECT TO NEO4J
    connection = Neo4jConnection(uri=uri, user=username, pwd=password)
    # log it
    logger.info(f"Neo4j connection established. neo4j vers: {connection.neo4j_version}")

    # retrieve import path
    neo_import_path = connection.abs_import_path()
    logger.info(f"DB import filepath: {neo_import_path}")

    ## MOVE FILES FROM source_folder TO DB IMPORT FOLDER
    logger.info(f"Copying files from {source_folder} to {neo_import_path}")
    copy_recursively(src=source_folder, dest=neo_import_path)

    ## RETRIEVE NODE AND EDGE LISTS (DATA AND HEADER CSVs)
    logger.info("Getting filepaths to node and edge lists")
    # getting header files to iterate through
    node_head_files = filter_filepaths(
        neo_import_path, identifiers=["-header.csv", "node"]
    )
    logger.info(f"Identified NODE header files: {node_head_files}")
    # getting data files
    node_data_files = filter_filepaths(neo_import_path, identifiers=["-data", "node"])
    logger.info(f"Identified NODE data files: {node_data_files}")
    edge_head_files = filter_filepaths(
        neo_import_path, identifiers=["-header.csv", "edge"]
    )
    logger.info(f"Identified EDGE header files: {edge_head_files}")
    # getting data files
    edge_data_files = filter_filepaths(neo_import_path, identifiers=["-data", "edge"])
    logger.info(f"Identified EDGE data files: {edge_data_files}")

    ## GENERATING NODE CYPHER LOADING QUERIES
    node_queries = cypher_query_load_nodes(
        header_files=node_head_files,
        data_files=node_data_files,
        num_transactions=num_transactions,
        sep=sep,
        quotechar=quotechar,
        fill_na=fill_na,
    )
    # change filename to file:///
    local_node_queries = connection.to_local_prefix(node_queries)
    # log it
    logger.info("NODE QUERIES:")
    for q in local_node_queries:
        logger.info(q)

    ## GENERATING EDGE CYPHER LOADING QUERIES
    edge_queries = cypher_query_load_edges(
        header_files=edge_head_files,
        data_files=edge_data_files,
        num_transactions=num_transactions,
        sep=sep,
        quotechar=quotechar,
        fill_na=fill_na,
    )
    # change filenames to file:///
    local_edge_queries = connection.to_local_prefix(edge_queries)
    # log it
    logger.info("EDGE QUERIES:")
    for q in local_edge_queries:
        logger.info(q)

    ## CREATE NODES IN NEO4J DB
    logger.info(f"Creating nodes in {db_name}")
    for q in local_node_queries:
        # run query in neo4j
        stdout = connection.query(query=q, db=db_name)
        # logit
        logger.info(stdout)

    ## CREATE EDGES IN NEO4J DB
    logger.info(f"Creating edges in {db_name}")
    for q in local_edge_queries:
        # run query in neo4j
        stdout = connection.query(query=q, db=db_name)
        # logit
        logger.info(stdout)

    # logit
    logger.info("Run Complete")

else:
    print("File imported instead of executed. Not completed.")
