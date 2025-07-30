import contextlib
import dataclasses
import urllib.parse
from typing import Any

import packaging.version
import psycopg
import pymysql
import sqlalchemy
import sqlalchemy.ext.compiler
import sqlalchemy.orm

from iker.common.utils.sequtils import head_or_none
from iker.common.utils.strutils import is_blank

__all__ = [
    "ConnectionMaker",
    "DBAdapter",
    "orm_to_dict",
    "orm_clone",
    "mysql_insert_ignore",
    "postgresql_insert_on_conflict_do_nothing",
]


class ConnectionMaker(object):
    """
    Provides utilities to simplify establishing database connections and sessions, including connection string
    construction, engine and session creation, and model management.

    :param driver: The database driver string (e.g., ``mysql+pymysql``).
    :param host: The database host.
    :param port: The database port.
    :param user: The database user.
    :param password: The database password.
    :param database: The database name.
    :param engine_opts: Optional dictionary of SQLAlchemy engine options.
    :param session_opts: Optional dictionary of SQLAlchemy session options.
    """

    class Drivers:
        Mysql = f"mysql+{pymysql.__name__}"
        Postgresql = f"postgresql+{psycopg.__name__}"

    def __init__(
        self,
        driver: str,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        engine_opts: dict[str, Any] | None = None,
        session_opts: dict[str, Any] | None = None,
    ):
        self.driver = driver
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.engine_opts = engine_opts or {}
        self.session_opts = session_opts or {}

    @staticmethod
    def from_url(
        driver: str,
        url: str | urllib.parse.ParseResult,
        engine_opts: dict[str, Any] | None = None,
        session_opts: dict[str, Any] | None = None,
    ) -> "ConnectionMaker":
        """
        Creates a ``ConnectionMaker`` instance from a URL string or ``ParseResult``, extracting connection parameters.

        :param driver: The database driver string.
        :param url: The database URL as a string or ``ParseResult``.
        :param engine_opts: Optional dictionary of SQLAlchemy engine options.
        :param session_opts: Optional dictionary of SQLAlchemy session options.
        :return: A ``ConnectionMaker`` instance.
        """
        if isinstance(url, str):
            return ConnectionMaker.from_url(driver, urllib.parse.urlparse(url), engine_opts, session_opts)
        if isinstance(url, urllib.parse.ParseResult):
            return ConnectionMaker(driver,
                                   url.hostname,
                                   url.port,
                                   url.username,
                                   url.password,
                                   url.path.strip("/"),
                                   engine_opts,
                                   session_opts)
        raise ValueError("malformed parameter 'url'")

    @property
    def connection_string(self) -> str:
        """
        Constructs the SQLAlchemy connection string for the database using the provided parameters.

        :return: The connection string as a string.
        """
        port_part = "" if self.port is None else (":%d" % self.port)
        user_part = urllib.parse.quote(self.user, safe="")
        password_part = "" if is_blank(self.password) else (":%s" % urllib.parse.quote(self.password, safe=""))
        database_part = urllib.parse.quote(self.database, safe="")

        return f"{self.driver}://{user_part}{password_part}@{self.host}{port_part}/{database_part}"

    @property
    def engine(self) -> sqlalchemy.Engine:
        """
        Returns a SQLAlchemy ``Engine`` instance for the configured connection string and engine options.

        :return: The SQLAlchemy ``Engine``.
        """
        return sqlalchemy.create_engine(self.connection_string, **self.engine_opts)

    def make_connection(self):
        """
        Establishes and returns a new database connection using the SQLAlchemy engine.

        :return: A database connection object.
        """
        return self.engine.connect()

    def make_session(self, **kwargs) -> contextlib.AbstractContextManager[sqlalchemy.orm.Session]:
        """
        Creates a context-managed SQLAlchemy session with the configured engine and session options.

        :param kwargs: Additional keyword arguments for session creation.
        :return: A context manager yielding a SQLAlchemy ``Session``.
        """
        return contextlib.closing(sqlalchemy.orm.sessionmaker(self.engine, **{**self.session_opts, **kwargs})())

    def create_model(self, orm_base):
        """
        Creates all tables defined in the given ORM base using the current engine.

        :param orm_base: The SQLAlchemy ORM base class.
        :return: None.
        """
        if packaging.version.parse(sqlalchemy.__version__) >= packaging.version.parse("2"):
            if not isinstance(orm_base, type) or not issubclass(orm_base, sqlalchemy.orm.DeclarativeBase):
                raise TypeError("not a subclass of 'sqlalchemy.orm.DeclarativeBase'")

        orm_base.metadata.create_all(self.engine)

    def drop_model(self, orm_base):
        """
        Drops all tables defined in the given ORM base using the current engine.

        :param orm_base: The SQLAlchemy ORM base class.
        :return: None.
        """
        if packaging.version.parse(sqlalchemy.__version__) >= packaging.version.parse("2"):
            if not isinstance(orm_base, type) or not issubclass(orm_base, sqlalchemy.orm.DeclarativeBase):
                raise TypeError("not a subclass of 'sqlalchemy.orm.DeclarativeBase'")

        orm_base.metadata.drop_all(self.engine)

    def execute(self, sql: str, **params):
        """
        Executes the given SQL statement with the specified parameters.

        :param sql: The SQL statement to execute.
        :param params: The parameters dictionary for the SQL statement.
        :return: None.
        """
        with self.make_connection() as connection:
            connection.execute(sqlalchemy.text(sql), params)
            connection.commit()

    def query_all(self, sql: str, **params) -> list[tuple]:
        """
        Executes the given SQL query with the specified parameters and returns all result tuples.

        :param sql: The SQL query to execute.
        :param params: The parameters dictionary for the SQL query.
        :return: A list of result tuples.
        """
        with self.make_connection() as connection:
            with contextlib.closing(connection.execute(sqlalchemy.text(sql), params)) as proxy:
                return [item for item in proxy.fetchall()]

    def query_first(self, sql: str, **params) -> tuple | None:
        """
        Executes the given SQL query with the specified parameters and returns the first result tuple, or ``None`` if no
        results are found.

        :param sql: The SQL query to execute.
        :param params: The parameters dictionary for the SQL query.
        :return: The first result tuple, or ``None`` if no results are found.
        """
        return head_or_none(self.query_all(sql, **params))


DBAdapter = ConnectionMaker


def orm_to_dict(orm, exclude: set[str] = None) -> dict[str, Any]:
    """
    Converts an ORM object to a dictionary, optionally excluding specified fields.

    :param orm: The ORM object to convert.
    :param exclude: An optional set of field names to exclude from the result.
    :return: A dictionary mapping field names to their values.
    """
    if packaging.version.parse(sqlalchemy.__version__) >= packaging.version.parse("2"):
        if not isinstance(orm, sqlalchemy.orm.DeclarativeBase):
            raise TypeError("not an instance of 'sqlalchemy.orm.DeclarativeBase'")

    mapper = sqlalchemy.inspect(type(orm))
    return dict((c.key, getattr(orm, c.key)) for c in mapper.columns if c.key not in (exclude or set()))


def orm_clone(orm, exclude: set[str] = None, no_autoincrement: bool = False):
    """
    Creates a clone of the given ORM object, optionally excluding specified fields or auto-increment fields.

    :param orm: The ORM object to clone.
    :param exclude: An optional set of field names to exclude from the clone.
    :param no_autoincrement: If ``True``, excludes auto-increment fields from the clone.
    :return: A new ORM object with the specified fields cloned.
    """
    if packaging.version.parse(sqlalchemy.__version__) >= packaging.version.parse("2"):
        if not isinstance(orm, sqlalchemy.orm.DeclarativeBase):
            raise TypeError("not an instance of 'sqlalchemy.orm.DeclarativeBase'")

    mapper = sqlalchemy.inspect(type(orm))
    exclude = exclude or (set(c.key for c in mapper.columns if c.autoincrement is True) if no_autoincrement else set())
    fields = orm_to_dict(orm, exclude)

    if not dataclasses.is_dataclass(orm):
        return type(orm)(**fields)

    init_fields = dict((field.name, fields.get(field.name)) for field in dataclasses.fields(orm) if field.init)

    new_orm = type(orm)(**init_fields)
    for name, value in fields.items():
        if name not in init_fields:
            setattr(new_orm, name, value)
    return new_orm


def mysql_insert_ignore(enabled: bool = True):
    """
    Registers a SQLAlchemy compiler extension to add ``IGNORE`` to MySQL ``INSERT`` statements if ``enabled``.

    :param enabled: Whether to enable the ``IGNORE`` prefix for MySQL ``INSERT`` statements.
    :return: None.
    """

    @sqlalchemy.ext.compiler.compiles(sqlalchemy.sql.Insert, "mysql")
    def dispatch(insert: sqlalchemy.sql.Insert, compiler: sqlalchemy.sql.compiler.SQLCompiler, **kwargs) -> str:
        if not enabled:
            return compiler.visit_insert(insert, **kwargs)

        return compiler.visit_insert(insert.prefix_with("IGNORE"), **kwargs)


def postgresql_insert_on_conflict_do_nothing(enabled: bool = True):
    """
    Registers a SQLAlchemy compiler extension to add ``ON CONFLICT DO NOTHING`` to PostgreSQL ``INSERT`` statements if
    ``enabled``.

    :param enabled: Whether to enable the ``ON CONFLICT DO NOTHING`` clause for PostgreSQL ``INSERT`` statements.
    :return: None.
    """

    @sqlalchemy.ext.compiler.compiles(sqlalchemy.sql.Insert, "postgresql")
    def dispatch(insert: sqlalchemy.sql.Insert, compiler: sqlalchemy.sql.compiler.SQLCompiler, **kwargs) -> str:
        if not enabled:
            return compiler.visit_insert(insert, **kwargs)

        statement = compiler.visit_insert(insert, **kwargs)
        # If we have a ``RETURNING`` clause, we must insert before it
        returning_position = statement.find("RETURNING")
        if returning_position >= 0:
            return statement[:returning_position] + " ON CONFLICT DO NOTHING " + statement[returning_position:]
        else:
            return statement + " ON CONFLICT DO NOTHING"
