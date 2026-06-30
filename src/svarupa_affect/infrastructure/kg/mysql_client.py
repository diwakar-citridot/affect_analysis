"""Shared MySQL connection helper for read-only KG adapters."""

from __future__ import annotations

import pymysql  # type: ignore[import-untyped]
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from ..config import Settings


def open_mysql(settings: Settings, *, database: str | None = None) -> Connection[DictCursor]:
    if not settings.mysql_host:
        raise RuntimeError("MySQL host not configured")
    db = database or settings.mysql_database
    if not db:
        raise RuntimeError("MySQL database not configured")
    return pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user or "",
        password=settings.mysql_password or "",
        database=db,
        charset="utf8mb4",
        connect_timeout=10,
        read_timeout=30,
        cursorclass=DictCursor,
    )
