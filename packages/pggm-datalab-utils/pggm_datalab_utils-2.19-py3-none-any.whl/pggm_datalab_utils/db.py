import json
import logging
import math
import os
import sqlite3
import struct
from contextlib import contextmanager
from datetime import datetime
import platform
from typing import Any, Dict, Hashable, Iterator, List, Optional, Union

import pyodbc
from azure.identity import AzureCliCredential, InteractiveBrowserCredential, ChainedTokenCredential

Connection = Union[
    pyodbc.Connection, sqlite3.Connection
]  # Todo: unify in own interface to get autocomplete
Cursor = Union[pyodbc.Cursor, sqlite3.Cursor]
Record = Dict[str, Any]
RecordList = List[Record]


def get_db_connection(server: str, database: str = None) -> Connection:
    """
    Initiate pyodbc connection to a SQL Server database.
    You may specify `DB_DRIVER` to a pyodbc-compatible driver name for your system. It defaults to
    `{ODBC Driver 17 for SQL Server}`. If you specify the value `SQLITE` the built-in sqlite3 library is used to
     connect instead.
    You may specify `DB_AUTH` in the environment to control the authentication. Normally, this will be the passed as
     the Authentication parameter in the ODBC connection string. However, if you specify "PGGMInteractive" as value,
     you will be prompted to log into a browser and authenticate to the database that way.
    You may specify `DB_UID` and `DB_PASSWORD` to request SQL-based authentication. This will only work if `DB_AUTH`
     is not specified.
    If you specify neither `DB_AUTH` nor `DB_UID`, a fallback approach is used. If the server is detected to be
     on-premise (SLP-xxxx) or a managed instance (sqlmi-xxx.database.windows.net), the default driver is switched
     to `{SQL Server}`, and a login attempt is made using `ActiveDirectoryIntegrated` authentication. The only exception
     exists for SLOs, where managed instance databases (sqlmi-xxx.database.windows.net) require the newer SQL driver.
     If this fails, token-based authentication with a browser pop-up is attempted instead.
    """
    driver = os.environ.get("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};"

    if 'DB_USE_MANAGED_ID' in os.environ or 'USE_MANAGED_ID' in os.environ:
        raise ValueError(
            "DB_USE_MANAGED_ID and USE_MANAGED_ID are no long supported. Use `DB_AUTH=ActiveDirectoryMsi` instead."
        )

    if driver == "SQLITE":
        logging.info(
            f"Connecting to SQLite database {database} because driver=SQLITE. Ignoring other options."
        )

        # Make sqlite3 somewhat well-behaved.
        sqlite3.register_converter(
            "datetime", lambda b: datetime.fromisoformat(b.decode())
        )
        sqlite3.register_converter("json", json.loads)
        sqlite3.register_adapter(list, json.dumps)
        sqlite3.register_adapter(dict, json.dumps)
        return sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)

    elif os.environ.get('DB_AUTH', False) == 'PGGMInteractive':
        logging.info(
            f"Logging into {database}/{server} using an Azure token"
        )
        entra_id_connect = get_database_token()
        return pyodbc.connect(connection_string, attrs_before=entra_id_connect)

    elif auth := os.environ.get('DB_AUTH', False):
        logging.info(f"Logging into {database}/{server} using {auth}.")
        connection_string += f'Authentication={auth};'
        return pyodbc.connect(connection_string)

    elif user := os.environ.get("DB_UID", False):
        logging.info(f"Logging into {database}/{server} as {user} using sql server authentication.")
        connection_string += (
            f'Uid={os.environ["DB_UID"]};Pwd={os.environ["DB_PASSWORD"]};'
        )
        return pyodbc.connect(connection_string)

    # Special case handling for making things "just work"
    else:
        machine_is_slo = platform.node().lower().startswith('slo')
        server_is_mi = server.lower().startswith('pggm-sqlmi')
        server_is_on_prem = server.lower().startswith('slp')

        # Fallback to old driver if on slo, but not connecting to managed instance
        #  or vice versa
        #  or not on slo but connecting to on-prem
        if ((machine_is_slo and not server_is_mi)
            or (not machine_is_slo and server_is_mi)
            or (not machine_is_slo and server_is_on_prem)):
            driver = os.environ.get("DB_DRIVER", "SQL Server")
            connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};"

        # In any case ADI is used for authentication
        authentication = "ActiveDirectoryIntegrated"
        connection_string += f"Authentication={authentication};"
        logging.info(
            f"Logging into {database}/{server} using {driver}, {authentication}."
        )

        try:
            return pyodbc.connect(connection_string)

        except Exception as e:  # Fall back on token-based auth
            logging.error(f'Error logging in {e}')

            if platform.node().upper().startswith('SLO'):
                driver = os.environ.get("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
            connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};"
            entra_id_connect = get_database_token()

            return pyodbc.connect(connection_string, attrs_before=entra_id_connect)



def get_database_token() -> dict:
    """Generate token for accessing Microsoft Azure SQL Database."""
    credential = ChainedTokenCredential(AzureCliCredential(), InteractiveBrowserCredential())
    token = credential.get_token('https://database.windows.net/.default')[0]
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    token_struct = struct.pack('=i', len(token * 2)) + ''.join(f'{c}\x00' for c in token).encode('utf-8')
    return {SQL_COPT_SS_ACCESS_TOKEN: token_struct}


@contextmanager
def cursor(db_server: str, db_name: str) -> Iterator[Cursor]:
    """
    Obtain a cursor for a certain database server and database name. Internally uses `get_db_connection`. Use this as
    a context manager, which will handle closing the cursor and the connection. NOTE: this will not handle transaction
    support: most of the time that means you need to commit your transactions yourself!
    Example usage:
    ```
    with cursor('my_server.net', 'test') as c:
        my_data = c.execute('select * from test_database').fetchall()
    ```
    """
    conn = get_db_connection(db_server, db_name)
    c = conn.cursor()
    try:
        if hasattr(c, 'fast_executemany'):
            c.fast_executemany = True
        yield c
    finally:
        c.close()
        conn.close()


def query(c: Cursor, sql: str, data: Optional[tuple] = None) -> RecordList:
    """
    Call `c.execute(sql, data).fetchall()` and format the resulting rowset a list of records of the form
    [{colname: value}].
    """
    if data is None:
        result = c.execute(sql).fetchall()
    else:
        result = c.execute(sql, data).fetchall()
    headers = [name for name, *_ in c.description]
    return [dict(zip(headers, r)) for r in result]


def get_all(c: Cursor, table_name: str) -> RecordList:
    """
    Get all current data from table `table_name`.

    IMPORTANT WARNING: `table_name` is not sanitized. Don't pass untrusted table names to this function!
    """
    return query(c, f'select * from {table_name}')


def validate(data: RecordList) -> RecordList:
    """Validate data records are uniform and have string keys, and replace nans with None."""
    assert len(unique := set(tuple(sorted(r.keys())) for r in data)) == 1, \
        f'Non-uniform list of dictionaries passed, got differing keys {unique}.'
    assert not any(non_str := {k: type(k) for k in data[0].keys() if not isinstance(k, str)}), \
        f'Non-string keys in data, got keys with types {non_str}.'
    return [{k: None if isinstance(v, float) and math.isnan(v) else v for k, v in r.items()} for r in data]


def insert_with_return(
        c: Cursor, table_name: str, data: Record, return_columns: Optional[Union[str, tuple]] = None
) -> Record:
    """
    Insert data into the database, returning a set of return columns. The primary use for this is if you have columns
    generated by your database, like an identity. Returns input record with returned columns added (if any).
    """
    validated_data, *_ = validate([data])
    return_columns = (return_columns,) if isinstance(return_columns, str) else return_columns

    columns = validated_data.keys()
    insert_data = tuple(validated_data[col] for col in columns)
    text_columns = ', '.join(columns)
    placeholders = ', '.join('?' for _ in columns)
    # Dispatch on cursor type for now, pyodbc type is for MSSQL only
    if return_columns is None:
        sql = f'insert into {table_name}({text_columns}) values ({placeholders})'
        c.execute(sql)
        return validated_data
    elif isinstance(c, sqlite3.Cursor):
        text_return_columns = ', '.join(return_columns)
        sql = f'insert into {table_name}({text_columns}) values ({placeholders}) returning {text_return_columns}'
        output = query(c, sql, insert_data)[0]
        return {**validated_data, **output}
    else:
        text_return_columns = ', '.join(f'Inserted.{col}' for col in return_columns)
        sql = f'insert into {table_name}({text_columns}) output {text_return_columns} values ({placeholders})'
        output = query(c, sql, insert_data)[0]
        return {**validated_data, **output}


def write(c: Cursor, table_name: str, data: RecordList, primary_key: Optional[Union[str, tuple]] = None, *,
          update=True, insert=True, delete=True):
    """
    Update data in database table. We check identity based on the keys of the IndexedPyFrame.
    `update`, `insert`, and `delete` control which actions to take. By default, this function emits the correct update,
    insert, and delete queries to make the database table equal to the in-memory table.
    - `update=True` means rows already in the database will be updated with the in-memory data
    - `insert=True` means rows not already in the database will be added from the in-memory data
    - `delete=True` means rows present in the database but not in the in-memory database will be deleted

    If primary_key is None, only inserting is supported.

    IMPORTANT WARNING: `table_name` is not sanitized. Don't pass untrusted table names to this function!
    """
    validated_data = validate(data)

    # Deal with primary key, list of writeable columns, indexed data, data in db
    if primary_key is None:
        assert not update and not delete, 'updating and deleting without specifying a primary key not supported'
        primary_key = tuple()
        validated_data = {i: r for i, r in enumerate(validated_data)}
        columns = tuple(k for k in validated_data[0].keys())
        in_db = set()
    else:
        primary_key = (primary_key,) if isinstance(primary_key, str) else tuple(primary_key)
        assert all(isinstance(r[k], Hashable) for r in validated_data for k in primary_key)
        if any(empty_strings := [name for name in validated_data[0].keys() if
                                 any(r[name] == '' for r in validated_data)]):
            logging.warning(f'Columns {empty_strings} contain empty strings. '
                            f'Generally inserting empty strings into a database is a bad idea.')

        # List of writeable columns (for updates we don't try to overwrite the primary key)
        columns = tuple(k for k in validated_data[0].keys() if k not in primary_key)

        # Indexed data on primary key
        validated_data = {tuple(r[i] for i in primary_key): r for r in validated_data}

        # Data present in database
        sql = f'select {", ".join(primary_key)} from {table_name}'
        in_db = {tuple(r[k] for k in primary_key) for r in query(c, sql)}

    if delete and (delete_keys := in_db - validated_data.keys()):
        condition = ' AND '.join(f'{k}=?' for k in primary_key)
        sql = f'delete from {table_name} where {condition}'

        c.executemany(sql, list(delete_keys))

    if update and (update_keys := validated_data.keys() & in_db):
        update_data = [
            (tuple(validated_data[k][col] for col in columns) + tuple(validated_data[k][col] for col in primary_key))
            for k in update_keys
        ]

        # Cannot use keyword placeholders because pyodbc doesn't support named paramstyle. Would be better.
        assignment = ', '.join(f'{col}=?' for col in columns)
        pk_cols = ' AND '.join(f'{col}=?' for col in primary_key)
        sql = f'update {table_name} set {assignment} where {pk_cols}'

        if columns:  # If columns is empty, there is nothing to update since we leave the primary key untouched
            c.executemany(sql, update_data)

    if insert and (insert_keys := validated_data.keys() - in_db):
        insert_data = [tuple(validated_data[k][col] for col in columns + primary_key) for k in insert_keys]

        placeholders = ', '.join(f'?' for _ in columns + primary_key)
        text_columns = ', '.join(columns + primary_key)
        sql = f'insert into {table_name}({text_columns}) VALUES ({placeholders})'

        c.executemany(sql, insert_data)
