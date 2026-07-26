from decimal import Decimal, InvalidOperation
from typing import Any

from alembic.runtime.migration import MigrationContext
from sqlalchemy import Column, Numeric


def _normalize_decimal_default(value: str | None) -> Decimal | None:
    if value is None:
        return None

    normalized = value.strip()

    while len(normalized) >= 2 and normalized.startswith("(") and normalized.endswith(")"):
        normalized = normalized[1:-1].strip()

    normalized = normalized.strip("'\"")

    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def compare_server_defaults(
    context: MigrationContext,
    inspected_column: Column[Any],
    metadata_column: Column[Any],
    inspected_default: str | None,
    _metadata_default: object,
    rendered_metadata_default: str | None,
) -> bool | None:
    if context.dialect.name != "mysql":
        return None

    if not isinstance(metadata_column.type, Numeric):
        return None

    inspected_value = _normalize_decimal_default(inspected_default)
    metadata_value = _normalize_decimal_default(rendered_metadata_default)

    if inspected_value is None or metadata_value is None:
        return None

    return inspected_value != metadata_value
