from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


class DatabaseConfigError(Exception):
    """Raised when auth.txt is missing or malformed."""


class DatabaseError(Exception):
    """Raised when a database operation fails."""


class Database:
    """
    Generic DB access layer for repositories.

    Responsibilities:
    - Load DB credentials from auth.txt
    - Create connections
    - Build generic CRUD SQL
    - Execute queries and return rows as dicts

    Repositories should:
    - call methods like fetch_one / fetch_all / insert / update / delete
    - map returned rows into domain dataclasses

    Expected auth.txt format (flexible):
        host=127.0.0.1
        port=3306
        user=root
        password=secret
        database=pii26_aureatech

    Also accepted:
        host: 127.0.0.1
        db=pii26_aureatech

    Lines starting with # are ignored.
    """

    _IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    _PACKAGE_ROOT = Path(__file__).resolve().parents[2]
    DEFAULT_AUTH_PATH = _PACKAGE_ROOT / "auth.txt"

    def __init__(self, auth_path: str | os.PathLike[str] | None = None):
        self.auth_path = Path(auth_path) if auth_path else self.DEFAULT_AUTH_PATH
        self.config = self._load_auth_file(self.auth_path)
        self.driver_name, self.driver = self._load_driver()

    # --------------------------------------------------
    # Driver / config
    # --------------------------------------------------
    def _load_driver(self):
        try:
            import mariadb  # type: ignore
            return "mariadb", mariadb
        except ImportError:
            try:
                import mysql.connector  # type: ignore
                return "mysql.connector", mysql.connector
            except ImportError as exc:
                raise DatabaseConfigError(
                    "No supported DB driver found. Install `mariadb` or `mysql-connector-python`."
                ) from exc

    def _load_auth_file(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise DatabaseConfigError(f"auth.txt not found at: {path}")

        parsed: dict[str, str] = {}

        with path.open("r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                elif ":" in line:
                    key, value = line.split(":", 1)
                else:
                    continue

                key = key.strip().lower()
                value = value.strip().strip('"').strip("'")
                parsed[key] = value

        host = parsed.get("host", parsed.get("server", "127.0.0.1"))
        port = int(parsed.get("port", "3306"))
        user = parsed.get("user", parsed.get("username"))
        password = parsed.get("password", parsed.get("pass", ""))
        database = parsed.get("database", parsed.get("db", parsed.get("schema")))

        missing = []
        if not user:
            missing.append("user")
        if not database:
            missing.append("database")

        if missing:
            raise DatabaseConfigError(
                f"auth.txt is missing required key(s): {', '.join(missing)}"
            )

        return {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }

    # --------------------------------------------------
    # Connection helpers
    # --------------------------------------------------
    def connect(self):
        try:
            return self.driver.connect(**self.config)
        except Exception as exc:
            raise DatabaseError(f"Could not connect to database: {exc}") from exc

    # --------------------------------------------------
    # Public CRUD API
    # --------------------------------------------------
    def fetch_one(
        self,
        *,
        table: str,
        columns: str | list[str] = "*",
        where: dict[str, Any] | None = None,
        order_by: str | list[str] | None = None,
    ) -> dict[str, Any] | None:
        sql, params = self._build_select(
            table=table,
            columns=columns,
            where=where,
            order_by=order_by,
            limit=1,
        )

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            row = cur.fetchone()
            if row is None:
                return None
            return self._row_to_dict(cur, row)
        except Exception as exc:
            raise DatabaseError(f"DB fetch_one failed: {exc}\nSQL: {sql}") from exc
        finally:
            cur.close()
            conn.close()

    def fetch_all(
        self,
        *,
        table: str,
        columns: str | list[str] = "*",
        where: dict[str, Any] | None = None,
        order_by: str | list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        sql, params = self._build_select(
            table=table,
            columns=columns,
            where=where,
            order_by=order_by,
            limit=limit,
        )

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [self._row_to_dict(cur, row) for row in rows]
        except Exception as exc:
            raise DatabaseError(f"DB fetch_all failed: {exc}\nSQL: {sql}") from exc
        finally:
            cur.close()
            conn.close()

    def insert(self, *, table: str, data: dict[str, Any]) -> int:
        if not data:
            raise DatabaseError("insert() requires non-empty data")

        table_sql = self._validate_identifier(table)
        columns = [self._validate_identifier(col) for col in data.keys()]
        values = list(data.values())

        columns_sql = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        sql = f"INSERT INTO {table_sql} ({columns_sql}) VALUES ({placeholders})"

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql, tuple(values))
            conn.commit()
            return int(cur.lastrowid)
        except Exception as exc:
            conn.rollback()
            raise DatabaseError(f"DB insert failed: {exc}\nSQL: {sql}") from exc
        finally:
            cur.close()
            conn.close()

    def update(
        self,
        *,
        table: str,
        data: dict[str, Any],
        where: dict[str, Any] | None = None,
    ) -> int:
        if not data:
            raise DatabaseError("update() requires non-empty data")
        if not where:
            raise DatabaseError("update() requires a WHERE clause")

        table_sql = self._validate_identifier(table)

        set_parts = []
        params: list[Any] = []

        for col, value in data.items():
            col_sql = self._validate_identifier(col)
            if value is None:
                set_parts.append(f"{col_sql} = NULL")
            else:
                set_parts.append(f"{col_sql} = %s")
                params.append(value)

        where_sql, where_params = self._build_where(where)
        params.extend(where_params)

        sql = f"UPDATE {table_sql} SET {', '.join(set_parts)}{where_sql}"

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql, tuple(params))
            conn.commit()
            return cur.rowcount
        except Exception as exc:
            conn.rollback()
            raise DatabaseError(f"DB update failed: {exc}\nSQL: {sql}") from exc
        finally:
            cur.close()
            conn.close()

    def delete(self, *, table: str, where: dict[str, Any] | None = None) -> int:
        if not where:
            raise DatabaseError("delete() requires a WHERE clause")

        table_sql = self._validate_identifier(table)
        where_sql, params = self._build_where(where)

        sql = f"DELETE FROM {table_sql}{where_sql}"

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount
        except Exception as exc:
            conn.rollback()
            raise DatabaseError(f"DB delete failed: {exc}\nSQL: {sql}") from exc
        finally:
            cur.close()
            conn.close()

    def exists(self, *, table: str, where: dict[str, Any]) -> bool:
        row = self.fetch_one(
            table=table,
            columns=["1"],
            where=where,
        )
        return row is not None

    def count(self, *, table: str, where: dict[str, Any] | None = None) -> int:
        row = self.fetch_one(
            table=table,
            columns="COUNT(*) AS total",
            where=where,
        )
        return int(row["total"]) if row else 0

    # --------------------------------------------------
    # Internal SQL builders
    # --------------------------------------------------
    def _build_select(
        self,
        *,
        table: str,
        columns: str | list[str] = "*",
        where: dict[str, Any] | None = None,
        order_by: str | list[str] | None = None,
        limit: int | None = None,
    ) -> tuple[str, tuple[Any, ...]]:
        table_sql = self._validate_identifier(table)
        columns_sql = self._build_columns(columns)
        where_sql, params = self._build_where(where)
        order_sql = self._build_order_by(order_by)
        limit_sql = self._build_limit(limit)

        sql = f"SELECT {columns_sql} FROM {table_sql}{where_sql}{order_sql}{limit_sql}"
        return sql, params

    def _build_columns(self, columns: str | list[str]) -> str:
        if isinstance(columns, str):
            if columns == "*":
                return columns
            # allow safe SQL aliasing expressions like COUNT(*) AS total
            return columns

        if not columns:
            return "*"

        return ", ".join(self._validate_identifier(col) for col in columns)

    def _build_where(
        self,
        where: dict[str, Any] | None,
    ) -> tuple[str, tuple[Any, ...]]:
        if not where:
            return "", ()

        clauses: list[str] = []
        params: list[Any] = []

        for col, value in where.items():
            col_sql = self._validate_identifier(col)

            if value is None:
                clauses.append(f"{col_sql} IS NULL")
            elif isinstance(value, (list, tuple, set)):
                sequence = list(value)
                if not sequence:
                    clauses.append("1 = 0")
                else:
                    placeholders = ", ".join(["%s"] * len(sequence))
                    clauses.append(f"{col_sql} IN ({placeholders})")
                    params.extend(sequence)
            else:
                clauses.append(f"{col_sql} = %s")
                params.append(value)

        return " WHERE " + " AND ".join(clauses), tuple(params)

    def _build_order_by(self, order_by: str | list[str] | None) -> str:
        if not order_by:
            return ""

        if isinstance(order_by, str):
            parts = [order_by]
        else:
            parts = order_by

        cleaned_parts: list[str] = []
        for part in parts:
            token = part.strip()
            chunks = token.split()

            if len(chunks) == 1:
                col = self._validate_identifier(chunks[0])
                cleaned_parts.append(col)
            elif len(chunks) == 2 and chunks[1].upper() in {"ASC", "DESC"}:
                col = self._validate_identifier(chunks[0])
                direction = chunks[1].upper()
                cleaned_parts.append(f"{col} {direction}")
            else:
                raise DatabaseError(f"Invalid ORDER BY clause: {part}")

        return " ORDER BY " + ", ".join(cleaned_parts)

    def _build_limit(self, limit: int | None) -> str:
        if limit is None:
            return ""
        if limit <= 0:
            raise DatabaseError("LIMIT must be > 0")
        return f" LIMIT {int(limit)}"

    # --------------------------------------------------
    # Internal utilities
    # --------------------------------------------------
    def _validate_identifier(self, identifier: str) -> str:
        if not self._IDENTIFIER_RE.fullmatch(identifier):
            raise DatabaseError(f"Unsafe SQL identifier: {identifier}")
        return identifier

    @staticmethod
    def _row_to_dict(cursor, row: Any) -> dict[str, Any]:
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        if isinstance(row, dict):
            return row

        return dict(zip(columns, row))

    # --------------------------------------------------
    # Optional raw SQL fallback
    # --------------------------------------------------
    def execute(
        self,
        sql: str,
        params: tuple[Any, ...] | list[Any] | None = None,
        *,
        commit: bool = True,
    ) -> int:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql, params or ())
            if commit:
                conn.commit()
            return cur.rowcount
        except Exception as exc:
            conn.rollback()
            raise DatabaseError(f"DB execute failed: {exc}\nSQL: {sql}") from exc
        finally:
            cur.close()
            conn.close()


_db_instance: Database | None = None


def get_db(auth_path: str | os.PathLike[str] | None = None) -> Database:
    """
    Singleton-style accessor for repositories.

    Example:
        db = get_db()
        row = db.fetch_one(
            table=\"user\",
            where={\"email\": \"test@example.com\"}
        )
    """
    global _db_instance

    if _db_instance is None:
        _db_instance = Database(auth_path=auth_path)

    return _db_instance