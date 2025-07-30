import importlib.metadata
import logging

postgresql_access_logger = logging.getLogger(__name__)

__version__ = importlib.metadata.version('postgresql_access')

from postgresql_access.database import AbstractDatabase, DatabaseConfig, DatabaseDict, ReadOnlyCursor, NewTransactionCursor
from postgresql_access.database import SelfCloseCursor, SelfCloseConnection
