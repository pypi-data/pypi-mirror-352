"""Some utilities for generating Markdown."""

from contextlib import contextmanager
from typing import Optional


def generate_markdown_table(
    id: str,
    data: list[tuple[str, float]],
    caption: str,
    short_caption: Optional[str] = None,
) -> str:
    """Generate a Markdown table for a given centrality metric."""
    output: list[str] = []

    output.append(f"\n<!-- BEGIN {id} -->")
    output.append(
        f"table: {caption} {{#tbl:{id}{(' shortcaption="' + short_caption + '"') if short_caption else ''}}}\n"
    )
    output.append("| Package | Score |")
    output.append(f"|{FULL_WIDTH_HEADER_SEPARATOR}|------:|")
    for i, (pkg, score) in enumerate(data, 1):
        output.append(f"| {table_margin_marker(i)}`{pkg}` | {score:.4f} |")
    output.append(f"\n<!-- END {id} -->")

    return "\n".join(output)


@contextmanager
def surround_with_marker(marker: str):
    try:
        print(f"\n<!-- BEGIN {marker} -->\n")
        yield marker
    finally:
        print(f"\n<!-- END {marker} -->\n")


FULL_WIDTH_HEADER_SEPARATOR = "-" * 80


def table_margin_marker(marker: int):
    return f"\\marginnote{{\\scriptsize{{  {marker} }}}}" if marker % 5 == 0 else ""
