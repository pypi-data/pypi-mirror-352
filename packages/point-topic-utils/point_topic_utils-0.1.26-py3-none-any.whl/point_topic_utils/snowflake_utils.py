from .db.snowflake import SnowflakeDB
import pandas as pd


def query_to_df(query: str) -> pd.DataFrame:
    """
    Executes a SQL query and returns the results as a Pandas DataFrame.
    Handles connection management internally.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        pd.DataFrame: Query results as a DataFrame
        
    Example:
        ```python
        from point_topic_utils import query_to_df
        df = query_to_df("SELECT * FROM my_table LIMIT 10")
        ```
    """
    db = SnowflakeDB()
    try:
        db.connect()
        return db.query_to_df(query)
    finally:
        db.close_connection()


def execute_ddl(statement: str):
    """
    Executes a DDL statement (CREATE, ALTER, DROP, etc.).
    Handles connection management internally.
    
    Args:
        statement (str): DDL statement to execute
        
    Returns:
        The result of the statement execution or raises an exception on error
        
    Example:
        ```python
        from point_topic_utils import execute_ddl
        result = execute_ddl("CREATE TABLE test (id INT, name STRING)")
        ```
    """
    db = SnowflakeDB()
    try:
        db.connect()
        return db.execute_ddl(statement)
    finally:
        db.close_connection()


# Re-export for easier imports
__all__ = ['query_to_df', 'execute_ddl']
