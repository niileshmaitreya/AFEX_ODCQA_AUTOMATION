from __future__ import annotations
import os
import pyodbc
from queue import Queue


class MSSQLClient:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        pool_size: int = 3,
        driver: str = "ODBC Driver 17 for SQL Server"
    ):
        self._conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )

        self._pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self._pool.put(self._create_connection())

    def _create_connection(self):
        return pyodbc.connect(self._conn_str)

    def _get_connection(self):
        return self._pool.get()

    def _return_connection(self, conn):
        self._pool.put(conn)

    def query_scalar(self, sql: str, params: tuple | None = None):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            self._return_connection(conn)

    def query_all(self, sql: str, params: tuple | None = None):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            self._return_connection(conn)

    @classmethod
    def from_env(cls) -> "MSSQLClient":
        return cls(
            host=os.getenv("MSSQL_HOST"),
            port=int(os.getenv("MSSQL_PORT", "1433")),
            user=os.getenv("MSSQL_USER"),
            password=os.getenv("MSSQL_PASSWORD"),
            database=os.getenv("MSSQL_DATABASE", "master"),
        )