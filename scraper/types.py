from typing import TypedDict


class RequestMetaTypedDict(TypedDict):
    """TypedDict for request meta."""

    playwright: bool


class ElementPathsTypedDict(TypedDict):
    """TypedDict for path elements for selectors."""

    rows: str
    ip: str
    port: str
    protocol: str
    country: str
    anonymity: str
