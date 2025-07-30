#!/usr/bin/env python3

import configparser
import getpass
import os
import pwd
from abc import ABC, abstractmethod
from typing import Mapping, Any

import keyring

# Compatibility layer for psycopg2 and psycopg3
try:
    import psycopg
    psycopg_module = 'psycopg3'
    connect = psycopg.connect
    OperationalError = psycopg.OperationalError
except ImportError:
    import psycopg2 as psycopg
    psycopg_module = 'psycopg2'
    connect = psycopg.connect
    OperationalError = psycopg.OperationalError


class AbstractDatabase(ABC):
    __DATABASE = 'database'

    def __init__(self):
        self._app_name = 'Python app'
        self.schema = None
        self.port = 5432
        self._sslmode = None

    @abstractmethod
    def host(self) -> str: pass

    @abstractmethod
    def database_name(self) -> str: pass

    @abstractmethod
    def user(self) -> str: pass

    @abstractmethod
    def password(self) -> str: pass

    def set_app_name(self, name):
        self._app_name = name

    def application_name(self):
        return self._app_name

    def require_ssl(self):
        self._sslmode = 'require'

    def connect_fail(self, database, user, password, schema):
        pass

    def connect_success(self, database, user, password, schema):
        pass

    def build_connection_kwargs(self, dbname, user, password):
        kwargs = dict(
            host=self.host(),
            dbname=dbname,
            user=user,
            password=password,
            port=self.port,
            application_name=self._app_name,
        )
        if self._sslmode:
            kwargs['sslmode'] = self._sslmode
        return kwargs

    def connect(self, *, database_name: str = None, application_name: str = None, schema: str = None, **kwargs):
        if application_name is not None:
            self.set_app_name(application_name)
        dbname = database_name or self.database_name()
        user = self.user()
        password = self.password()

        try:
            conn = connect(**self.build_connection_kwargs(dbname, user, password), **kwargs)
            self.connect_success(dbname, user, password, schema)
        except OperationalError:
            self.connect_fail(dbname, user, password, schema)
            raise

        if schema:
            with conn.cursor() as cursor:
                cursor.execute(f"SET search_path TO {schema}")
            conn.commit()

        return conn

class DatabaseSimple(AbstractDatabase):
    def __init__(self, *, host: str, port: int = 5432, user: str, database_name: str):
        super().__init__()
        self._host = host
        self.port = port
        self.username = user
        self._dbname = database_name

    def host(self) -> str: return self._host
    def database_name(self) -> str: return self._dbname

    def user(self) -> str:
        if not self.username:
            u = input("database user: ")
            self.username = u.strip()
        return self.username

    @property
    def service_name(self):
        return f"Database {self.host()}.{self.database_name()}"

    def set_password(self, password) -> None:
        keyring.set_password(self.service_name, self.user(), password)

    def password(self) -> str:
        if (pw := keyring.get_password(self.service_name, self.user())) is not None:
            return pw
        pw = getpass.getpass(f"Enter password for {self.service_name} {self.user()}")
        return pw

    def connect_success(self, database, user, password, schema):
        self.set_password(password)
        super().connect_success(database, user, password, schema)

class DatabaseDict(DatabaseSimple):
    def __init__(self, *, dictionary: Mapping):
        host = dictionary['host']
        user = dictionary.get('user', None)
        if user == 'linux user':
            user = pwd.getpwuid(os.geteuid()).pw_name
        dbname = dictionary['database']
        port = int(dictionary.get('port', 5432))
        super().__init__(host=host, port=port, user=user, database_name=dbname)

class DatabaseConfig(DatabaseDict):
    def __init__(self, *, config: 'configparser.ConfigParser', section_key: str = 'database',
                 application_name: str = None):
        config_section = config[section_key]
        super().__init__(dictionary=config_section)
        self.set_app_name(application_name)

class SelfCloseConnection:
    def __init__(self, conn): self._conn = conn
    def __enter__(self): return self._conn
    def __exit__(self, exc_type, exc_val, exc_tb): self._conn.close()

class SelfCloseCursor:
    def __init__(self, conn): self._conn = conn
    def __enter__(self): return self._conn.cursor()
    def __exit__(self, exc_type, exc_val, exc_tb): self._conn.close()
    @property
    def connection(self): return self._conn

class ReadOnlyCursor:
    def __init__(self, conn, cursor_factory=None):
        self._conn = conn
        self._factory = cursor_factory

    def __enter__(self):
        self.existing_readonly = self._conn.readonly
        self._conn.readonly = True
        self._curs = self._conn.cursor(cursor_factory=self._factory)
        return self._curs

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._curs.close()
        self._conn.rollback()
        self._conn.readonly = self.existing_readonly

    @property
    def connection(self): return self._conn

class NewTransactionCursor:
    def __init__(self, conn, cursor_factory=None):
        self._conn = conn
        self._factory = cursor_factory

    def __enter__(self):
        self._conn.rollback()
        return self._conn.cursor(cursor_factory=self._factory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._conn.rollback()
        else:
            self._conn.commit()

    @property
    def connection(self): return self._conn

class Qobject:
    def __str__(self) -> str:
        return ''.join(f"{k}: {v}\n" for k, v in self.__dict__.items() if not k.startswith('_'))

def query_to_object(cursor, query: str) -> list:
    cursor.execute(query)
    return cursor_to_objects(cursor)

def cursor_to_objects(cursor) -> list:
    rval = []
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    for r in rows:
        qo = Qobject()
        for col, val in zip(cols, r):
            setattr(qo, col, val)
        rval.append(qo)
    return rval

def update_object_in_database(cursor: Any, obj, table: str, key: str) -> None:
    query = f"UPDATE {table} SET "
    sets, values, keyvalue = [], [], None
    for field, value in obj.__dict__.items():
        if field != key:
            sets.append(f"{field} = %s")
            values.append(value)
        else:
            keyvalue = value
    if keyvalue is None:
        raise ValueError(f"Key attribute {key} not found")
    query += ','.join(sets) + f" WHERE {key} = %s"
    values.append(keyvalue)
    cursor.execute(query, values)
    if cursor.rowcount != 1:
        raise ValueError(f"No update for {table}.{key} value {keyvalue}")

def row_estimate(connection, table: str) -> int:
    with connection.cursor() as curs:
        curs.execute("""SELECT reltuples::bigint FROM pg_catalog.pg_class WHERE relname = %s""", (table,))
        row = curs.fetchone()
        return int(row[0])

