from typing import NamedTuple


class SourceInfo(NamedTuple):
    """A tuple for source info to pass to the parser."""

    parser_class: str
    source_id: int
