from blitzdb.backends.sql import Backend as BlitzDBSQLBackend
from typing import Any, Optional, Dict
import logging
from contextlib import contextmanager
from ..helpers.exceptions import DatabaseError

logger = logging.getLogger(__name__)

Backend = BlitzDBSQLBackend
