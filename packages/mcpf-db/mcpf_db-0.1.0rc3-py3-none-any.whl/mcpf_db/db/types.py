from dataclasses import dataclass
from typing import Any


@dataclass
class DbConfig:
    """
    A configuration class for database connection settings.

    Attributes:
        driver (str | None): The database driver to use. Defaults to None.
        host (str): The hostname or IP address of the database server. Defaults to None.
        database (str | None): The name of the database to connect to. Defaults to None.
        user (str | None): The username for database authentication. Defaults to None.
        password (str | None): The password for database authentication. Defaults to None.
        port (str | None): The port number on which the database server is listening. Defaults to None in order to use the default port.
        config (dict[str, str] | None): Additional configuration options as key-value pairs. Defaults to None.
    """

    driver: str | None = None
    host: str | None = None
    database: str | None = None
    user: str | None = None
    password: str | None = None
    port: str | None = None
    config: dict[str, str] | None = None


@dataclass
class DbColumn:
    """
    A class representing a column in a database table.

    Attributes:
        name (str): The name of the column.
        type (str): The data type of the column.
        min (int | None): The minimum precision value allowed for the column if applicable. Defaults to None.
        max (int | None): The maximum precision value allowed for the column or the length. Defaults to None.
        nullable (bool): Indicates whether the column can contain NULL values. Defaults to True.
        default (Any): The default value for the column. Defaults to None.
    """

    name: str
    type: str
    min: int | None = None
    max: int | None = None
    nullable: bool = True
    default: Any = None
