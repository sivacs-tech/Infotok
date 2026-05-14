from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.models.domain import Base


def ensure_database_schema(engine: Engine):
    """Create new tables and add columns needed by newer app versions.

    SQLAlchemy's create_all creates missing tables, but it does not alter tables
    that already exist. Railway Postgres may still have an older MVP schema, so
    we add backward-compatible nullable/default columns before app startup code
    queries the ORM.
    """

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    dialect = engine.dialect.name

    with engine.begin() as connection:
        _ensure_columns(
            connection,
            inspector,
            dialect,
            "users",
            {
                "display_name": "VARCHAR",
                "avatar_url": "VARCHAR",
                "bio": "TEXT DEFAULT ''",
                "is_guest": _boolean_type(dialect, default=True),
                "created_at": _datetime_type(dialect),
            },
        )
        _ensure_columns(
            connection,
            inspector,
            dialect,
            "reels",
            {
                "caption": "TEXT DEFAULT ''",
                "thumbnail_url": "VARCHAR",
                "is_deleted": _boolean_type(dialect, default=False),
            },
        )
        _ensure_columns(
            connection,
            inspector,
            dialect,
            "interactions",
            {
                "created_at": _datetime_type(dialect),
            },
        )

        connection.execute(
            text("UPDATE users SET display_name = username WHERE display_name IS NULL")
        )
        connection.execute(text("UPDATE users SET bio = '' WHERE bio IS NULL"))
        connection.execute(
            text(f"UPDATE users SET is_guest = {_true_literal(dialect)} WHERE is_guest IS NULL")
        )
        connection.execute(
            text(
                "UPDATE users SET created_at = CURRENT_TIMESTAMP "
                "WHERE created_at IS NULL"
            )
        )
        connection.execute(text("UPDATE reels SET caption = '' WHERE caption IS NULL"))
        connection.execute(
            text(
                f"UPDATE reels SET is_deleted = {_false_literal(dialect)} "
                "WHERE is_deleted IS NULL"
            )
        )
        connection.execute(
            text(
                "UPDATE interactions SET created_at = CURRENT_TIMESTAMP "
                "WHERE created_at IS NULL"
            )
        )


def _ensure_columns(connection, inspector, dialect: str, table: str, columns: dict[str, str]):
    table_names = set(inspector.get_table_names())
    if table not in table_names:
        return

    existing = {column["name"] for column in inspector.get_columns(table)}
    for name, column_type in columns.items():
        if name not in existing:
            connection.execute(
                text(f"ALTER TABLE {table} ADD COLUMN {name} {column_type}")
            )


def _boolean_type(dialect: str, default: bool) -> str:
    literal = _true_literal(dialect) if default else _false_literal(dialect)
    return f"BOOLEAN DEFAULT {literal}"


def _datetime_type(dialect: str) -> str:
    return "TIMESTAMP" if dialect == "postgresql" else "DATETIME"


def _true_literal(dialect: str) -> str:
    return "TRUE" if dialect == "postgresql" else "1"


def _false_literal(dialect: str) -> str:
    return "FALSE" if dialect == "postgresql" else "0"
