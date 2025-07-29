import snowflake.connector
import pandas as pd

from ..get_secrets import get_secrets

class SnowflakeDB:
    """
    Class for connecting to the Snowflake database.
    
    Example usage:
        `db = SnowflakeDB()`
        `db.connect()`
        `result = db.execute_query(sql_query)`
        `db.close_connection()`

    Attributes:
        user (str): Snowflake user.
        password (str): Snowflake password.
        account (str): Snowflake account.
        warehouse (str): Snowflake warehouse.
        database (str): Snowflake database.
        schema (str): Snowflake schema.
        connection (snowflake.connector.connection.SnowflakeConnection): Snowflake connection.
    """
    def __init__(self):
        secret_name = "snowflake_developer_credentials"
        secrets = get_secrets(secret_name)

        self.user = secrets.get('user')
        self.password = secrets.get('password')
        self.account = secrets.get('account')
        self.warehouse = secrets.get('warehouse')
        self.database = secrets.get('database')
        self.schema = secrets.get('schema')

        if not all([self.user, self.password, self.account, self.warehouse, self.database, self.schema]):
             missing = [k for k, v in secrets.items() if v is None and k in ['user', 'password', 'account', 'warehouse', 'database', 'schema']]
             raise ValueError(f"Missing required Snowflake credentials in secret '{secret_name}': {', '.join(missing)}")

        self.connection = None

    def connect(self):
        """Establishes a connection to the Snowflake database."""
        print("Connecting to Snowflake...")
        self.connection = snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema
        )
        print("Snowflake connection established.")

    def close_connection(self):
        """Closes the Snowflake database connection."""
        if self.connection is not None:
            self.connection.close()
            print("Snowflake connection closed.")

    def query_to_df(self, query: str) -> pd.DataFrame:
        """Executes a given SQL query and returns the results as a Pandas DataFrame."""
        if self.connection is None:
            raise ConnectionError("Snowflake connection not established.")
        print(f"Executing query: {query}")
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            df = cursor.fetch_pandas_all()
            print(f"Query returned {len(df)} rows.")
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            cursor.close()

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
            from point_topic_utils.db.snowflake import execute_ddl
            result = execute_ddl("CREATE TABLE test (id INT, name STRING)")
            ```
        """
        db = SnowflakeDB()
        try:
            db.connect()
            if db.connection is None:
                raise ConnectionError("Snowflake connection not established.")
            
            print(f"Executing DDL statement: {statement}")
            cursor = db.connection.cursor()
            try:
                result = cursor.execute(statement)
                print("DDL statement executed successfully.")
                return result
            except Exception as e:
                print(f"Error executing DDL statement: {e}")
                raise
            finally:
                cursor.close()
                
        finally:
            db.close_connection() 