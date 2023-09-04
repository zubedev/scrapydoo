from typing import TypedDict


class FlareSolverrSolutionTypedDict(TypedDict):
    """TypedDict for FlareSolverr solution."""

    url: str
    status: int
    headers: dict[str, str]
    response: str
    cookies: dict[str, str] | list[dict[str, str]]
    userAgent: str


class FlareSolverrResponseTypedDict(TypedDict):
    """TypedDict for FlareSolverr response."""

    solution: FlareSolverrSolutionTypedDict
    status: str
    message: str
    startTimestamp: int
    endTimestamp: int
    version: str


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
