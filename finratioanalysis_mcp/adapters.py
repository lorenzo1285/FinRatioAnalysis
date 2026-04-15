"""Data adapters for converting pandas DataFrames to MCP response formats.

Handles both JSON and Markdown output per FR-013, with NaN→null conversion
per FR-004 and ISO-8601 date formatting per FR-003.

Numeric precision: Markdown renderers use `:.6g` to preserve ≥6 significant
digits per FR-004. JSON output preserves full pandas precision verbatim.
"""

from typing import Any

import pandas as pd


def _fmt_number(value: float) -> str:
    """Format a number with 6 significant digits (FR-004)."""
    return f"{value:.6g}"


def df_to_period_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert time-series DataFrame to list of period dictionaries.

    Transforms DataFrame index to ISO-8601 'date' field, converts NaN to None.
    The first column of the reset DataFrame is always treated as the date —
    its original name (if any) is discarded to guarantee the 'date' key.

    Args:
        df: DataFrame with datetime index and numeric columns

    Returns:
        List of dictionaries, one per row, with 'date' + metric fields

    Example:
        >>> df = pd.DataFrame({'ROE': [0.15, 0.18]},
        ...                   index=pd.to_datetime(['2023-01-01', '2024-01-01']))
        >>> df_to_period_rows(df)
        [{'date': '2023-01-01', 'ROE': 0.15}, {'date': '2024-01-01', 'ROE': 0.18}]
    """
    df_copy = df.reset_index()

    # First column is always the former index; force-rename to 'date' regardless
    # of its original name. Safe because no library method emits a column named
    # 'date' in its data columns.
    df_copy.columns = ["date"] + list(df_copy.columns[1:])

    # Format date column as ISO-8601 string
    if pd.api.types.is_datetime64_any_dtype(df_copy["date"]):
        df_copy["date"] = df_copy["date"].dt.strftime("%Y-%m-%d")

    records = df_copy.to_dict(orient="records")

    # Replace NaN with None (null in JSON)
    for record in records:
        for key, value in list(record.items()):
            if pd.isna(value):
                record[key] = None

    return records


def df_to_snapshot(df: pd.DataFrame) -> dict[str, Any]:
    """Convert single-row DataFrame to snapshot dictionary.

    The library contract (constitution Principle II) guarantees that snapshot
    methods return exactly one row. This function fails loudly if that
    invariant is violated, rather than silently dropping data.

    Args:
        df: DataFrame with exactly one row

    Returns:
        Dictionary with column names as keys, NaN converted to None

    Raises:
        ValueError: If the DataFrame does not have exactly one row.

    Example:
        >>> df = pd.DataFrame({'Symbol': ['AAPL'], 'PE_Ratio': [28.5]})
        >>> df_to_snapshot(df)
        {'Symbol': 'AAPL', 'PE_Ratio': 28.5}
    """
    if len(df) != 1:
        raise ValueError(
            f"df_to_snapshot expects exactly 1 row, got {len(df)}"
        )

    row = df.iloc[0]

    result: dict[str, Any] = {}
    for key, value in row.items():
        if pd.isna(value):
            result[key] = None
        else:
            result[key] = value

    return result


def to_markdown_table(rows: list[dict[str, Any]]) -> str:
    """Convert list of dictionaries to Markdown table.

    Floats are rendered with 6 significant digits (FR-004). None is rendered
    as the literal string 'null' to match the JSON path.

    Args:
        rows: List of dictionaries with consistent keys

    Returns:
        Markdown-formatted table string

    Example:
        >>> rows = [{'date': '2023-01-01', 'ROE': 0.15},
        ...         {'date': '2024-01-01', 'ROE': 0.18}]
        >>> print(to_markdown_table(rows))
        | date | ROE |
        | ---- | --- |
        | 2023-01-01 | 0.15 |
        | 2024-01-01 | 0.18 |
    """
    if not rows:
        return "No data available"

    headers = list(rows[0].keys())

    header_row = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["-" * max(3, len(h)) for h in headers]) + " |"

    data_rows = []
    for row in rows:
        values = []
        for header in headers:
            value = row.get(header)
            if value is None:
                values.append("null")
            elif isinstance(value, float):
                values.append(_fmt_number(value))
            else:
                values.append(str(value))
        data_rows.append("| " + " | ".join(values) + " |")

    return "\n".join([header_row, separator] + data_rows)


def to_markdown_kv(snapshot: dict[str, Any]) -> str:
    """Convert snapshot dictionary to Markdown key-value list.

    Floats are rendered with 6 significant digits (FR-004). None is rendered
    as the literal string 'null' to match the JSON path.

    Args:
        snapshot: Dictionary with metric names and values

    Returns:
        Markdown-formatted key-value list

    Example:
        >>> snapshot = {'Symbol': 'AAPL', 'PE_Ratio': 28.5, 'Dividend_Yield': None}
        >>> print(to_markdown_kv(snapshot))
        - **Symbol**: AAPL
        - **PE_Ratio**: 28.5
        - **Dividend_Yield**: null
    """
    if not snapshot:
        return "No data available"

    lines = []
    for key, value in snapshot.items():
        if value is None:
            formatted_value = "null"
        elif isinstance(value, float):
            formatted_value = _fmt_number(value)
        else:
            formatted_value = str(value)

        lines.append(f"- **{key}**: {formatted_value}")

    return "\n".join(lines)
