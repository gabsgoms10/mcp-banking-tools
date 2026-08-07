from collections.abc import Generator
from contextlib import contextmanager
import logging
from typing import Any

from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from src.config import settings

logger = logging.getLogger("mcp-banking-tools.db")

_pool: ThreadedConnectionPool | None = None


def init_db_pool() -> ThreadedConnectionPool:
    """Initializes a thread-safe connection pool for PostgreSQL."""
    global _pool
    if _pool is None or _pool.closed:
        logger.info(
            f"Initializing PostgreSQL connection pool to {settings.postgres_host}:{settings.postgres_port}"
        )
        _pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            cursor_factory=RealDictCursor,
        )
    return _pool


@contextmanager
def get_db_cursor() -> Generator[tuple[Any, Any], None, None]:
    """Context manager acquiring and releasing a connection from the pool safely."""
    pool = init_db_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            yield conn, cursor
    finally:
        pool.putconn(conn)
