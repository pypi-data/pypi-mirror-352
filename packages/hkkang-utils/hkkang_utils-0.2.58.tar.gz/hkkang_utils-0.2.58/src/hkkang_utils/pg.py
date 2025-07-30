import psycopg
import traceback

from typing import Any, List, Dict


class DBConnector:
    # Static attributes
    connector_cache = {}

    def __init__(self, db_id: str):
        self.db_id = db_id
        self.conn = None
        self.cur = None

    def __new__(cls, *args, **kwargs):
        db_id = kwargs.get("db_id", None)
        if not db_id in DBConnector.connector_cache.keys():
            DBConnector.connector_cache[db_id] = super(DBConnector, cls).__new__(cls)
        return DBConnector.connector_cache[db_id]

    def execute(self, sql: str) -> List[Any]:
        return self.cur.execute(sql)

    def fetchall(self) -> List[Any]:
        return self.cur.fetchall()

    def fetchall_with_col_names(self) -> List[Dict[str, Any]]:
        """Return a list of dictionaries with column names as keys and list of values as values"""
        rows = self.fetchall()
        col_names = [col.name for col in self.cur.description]
        assert len(col_names) == len(
            set(col_names)
        ), f"Column names are not unique, len({col_names}) vs len({set(col_names)})"
        assert len(rows) == 0 or len(rows[0]) == len(
            col_names
        ), f"Number of columns ({len(col_names)}) does not match number of rows ({len(rows[0])})"
        # Create a dictionary with column names as keys and list of values as values
        results: List[Dict[str, Any]] = []
        for row in rows:
            # Insert each column value of a row into the corresponding list
            results.append({col_name: value for col_name, value in zip(col_names, row)})
        return results

    def fetchone(self) -> List[Any]:
        return self.cur.fetchone()

    def execute_and_fetchall(self, sql: str) -> List[Any]:
        self.execute(sql)
        return self.fetchall()

    def execute_and_fetchall_with_col_names(self, sql: str) -> List[Dict[str, Any]]:
        self.execute(sql)
        return self.fetchall_with_col_names()

    def close(self) -> None:
        self.conn.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.conn.close()
        return True


class PostgresConnector(DBConnector):
    def __init__(self, user_id: str, passwd: str, host: str, port: str, db_id: str):
        super(PostgresConnector, self).__init__(db_id=db_id)
        self.connect(user_id, passwd, host, port, db_id)
        self.conn.autocommit = True

    def __new__(cls, *args, **kwargs):
        return super(PostgresConnector, cls).__new__(cls, *args, **kwargs)

    def connect(self, user_id, passwd, host, port, db_id):
        self.conn = psycopg.connect(
            f"user={user_id} password={passwd} host={host} port={port} dbname={db_id}"
        )
        self.cur = self.conn.cursor()

    def fetch_table_names(self) -> List[str]:
        sql = """
            SELECT *
            FROM pg_catalog.pg_tables
            WHERE schemaname != 'pg_catalog' AND 
                  schemaname != 'information_schema';
        """
        self.cur.execute(sql)
        tables = [
            f"{str(table[0].lower())}.{str(table[1].lower())}".replace("public.", "")
            for table in self.cur.fetchall()
        ]
        return tables

    def fetch_column_names(self, table_ref: str) -> List[str]:
        def table_name_contains_schema(table_ref):
            return "." in table_ref

        if table_name_contains_schema(table_ref):
            table_schema = table_ref.split(".")[0]
            table_name = table_ref.split(".")[1]
        else:
            table_schema = "public"
            table_name = table_ref
        sql = f"""
            SELECT *
            FROM
                information_schema.columns
            WHERE
                table_schema = '{table_schema}'
                AND table_name = '{table_name}';
            """
        self.execute(sql)
        return [str(col[3].lower()) for col in self.fetchall()]

    def fetch_column_types(self, table_ref: str) -> List[str]:
        def table_name_contains_schema(table_ref):
            return "." in table_ref

        if table_name_contains_schema(table_ref):
            table_schema = table_ref.split(".")[0]
            table_name = table_ref.split(".")[1]
        else:
            table_schema = "public"
            table_name = table_ref
        sql = f"""
            SELECT *
            FROM
                information_schema.columns
            WHERE
                table_schema = '{table_schema}'
                AND table_name = '{table_name}';
            """
        self.execute(sql)
        return [str(col[7].lower()) for col in self.fetchall()]
