"""Shared MySQL connection helper for read-only KG adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..config import Settings

if TYPE_CHECKING:
    from pymysql.connections import Connection
    from pymysql.cursors import DictCursor


def open_mysql(settings: Settings, *, database: str | None = None) -> Connection[DictCursor]:
    if not settings.mysql_host:
        raise RuntimeError("MySQL host not configured")
    db = database or settings.mysql_database
    if not db:
        raise RuntimeError("MySQL database not configured")
    try:
        import pymysql  # type: ignore[import-untyped]
        from pymysql.cursors import DictCursor
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyMySQL is required for MySQL-backed KG adapters. Install with: pip install PyMySQL"
        ) from exc
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
