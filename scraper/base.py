import random
import re
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any, Literal, overload

import requests
import scrapy
from scrapy import Request, Selector
from scrapy.http import TextResponse
from scrapy.selector import SelectorList

from scraper.agents import USER_AGENTS
from scraper.items import ProxyItem
from scraper.types import ElementPathsTypedDict, FlareSolverrResponseTypedDict, RequestMetaTypedDict


class BaseSpider(scrapy.Spider):  # type: ignore
    start_urls: list[str] | None = None  # must be set in subclass
    render_to_file = False  # for debugging
    use_flaresolverr = False  # for cloudflare challenge
    use_playwright = False  # for JS rendering

    def __init__(self, name: str = None, **kwargs: Any) -> None:  # type: ignore[assignment]
        super().__init__(name=name, **kwargs)
        self.paths: ElementPathsTypedDict = self.set_element_paths()
        self.ua: str = kwargs.get("ua", None)
        self.headers: dict[str, Any] = kwargs.get("headers", None)
        self.meta: RequestMetaTypedDict = kwargs.get("meta", None)
        self.cookies: dict[str, str] | list[dict[str, str]] = kwargs.get("cookies", None)

    def start_requests(self) -> Generator[scrapy.Request, Any, None]:
        if not self.start_urls:
            raise AttributeError("Crawling could not start: 'start_urls' not found or empty.")
        if isinstance(self.start_urls, str):
            self.start_urls = [self.start_urls]
        if self.use_flaresolverr:
            self.solve_challenge(self.start_urls[0])  # solve the challenge before crawling

        callback, cb_kwargs = self.get_callback()
        for url in self.start_urls:
            yield Request(
                url,
                callback=callback,
                headers=self.get_headers(),
                cookies=self.get_cookies(),
                meta=self.get_meta(),
                dont_filter=True,
                cb_kwargs=cb_kwargs,
            )

    def solve_challenge(self, url: str, **kwargs: Any) -> dict[str, str] | list[dict[str, str]] | None:
        if "FLARESOLVERR_URL" not in self.settings:
            self.log("FLARESOLVERR_URL not found in settings.py")
            return None

        response = requests.post(
            self.settings["FLARESOLVERR_URL"],
            json={"cmd": "request.get", "url": url},
            allow_redirects=True,
            **kwargs,
        )
        if not response.ok:
            self.log(f"FlareSolverr error: {response.text}")
            return None

        data: FlareSolverrResponseTypedDict = response.json()
        if solution := data.get("solution"):
            if "userAgent" in solution:
                self.ua = solution["userAgent"]
            if "cookies" in solution:
                self.cookies = data["solution"]["cookies"]
                return self.cookies

        self.log(f"FlareSolverr error: either solution or cookies not found: {data}")
        return None

    def get_callback(self) -> tuple[Callable, dict[str, Any] | None]:  # type: ignore[type-arg]
        """Return a tuple of callback function and callback keyword arguments."""
        return self.parse, None

    def get_cookies(self) -> dict[str, str] | list[dict[str, str]] | None:
        return self.cookies

    def get_user_agent(self, ua: str = "") -> str:
        if not self.ua:
            self.ua = ua or random.choice(USER_AGENTS)
        return self.ua

    def get_headers(self, **kwargs: Any) -> dict[str, str]:
        if not self.headers:
            self.headers = {"User-Agent": self.get_user_agent(ua=kwargs.pop("ua", None)), **kwargs}
        return self.headers

    def get_meta(self, **kwargs: Any) -> RequestMetaTypedDict:
        """Return a `RequestMetaTypedDict` of meta data for the request."""
        if not self.meta:
            self.meta = {"playwright": self.use_playwright, **kwargs}
        return self.meta

    def set_element_paths(self) -> ElementPathsTypedDict:
        """Return a `ElementPathsTypedDict` of path elements for selectors.

        Example:
            return {
                "rows": "//tbody/tr",
                "ip": "./td[1]/span/text()",
                "port": "./td[2]/span/text()",
                "protocol": "./td[3]/span/text()",  (optional)
                "country": "./td[4]/span/text()",  (optional)
                "anonymity": "./td[5]/span/text()",  (optional)
            }
        """
        raise NotImplementedError("Please implement this method in your subclass.")

    def write_to_file(self, response: TextResponse) -> None:
        # write the response to a file for debugging
        Path(f"{self.name}.html").write_bytes(response.body)

    def parse(self, response: TextResponse, **kwargs: Any) -> Generator[dict[str, Any], Any, None]:
        """Parse the response and return a generator of ProxyItem."""
        if self.render_to_file:
            self.write_to_file(response)
            return

        rows = self.get_rows(response, self.paths["rows"])

        for r in rows:
            yield ProxyItem(
                ip=self.parse_ip_address(r),
                port=self.parse_port(r),
                protocol=self.parse_protocol(r),
                country=self.parse_country(r),
                anonymity=self.parse_anonymity(r),
                source=self.name,
            )

    def get_rows(self, response: TextResponse, xpath: str | None = None) -> SelectorList[Selector]:
        return response.xpath(xpath or self.paths["rows"])

    @overload
    def get_data(self, row: Selector, xpath: str, many: Literal[False] = False) -> str:
        ...

    @overload
    def get_data(self, row: Selector, xpath: str, many: Literal[True]) -> list[str]:
        ...

    def get_data(self, row: Selector, xpath: str, many: bool = False) -> str | list[str]:
        selector = row.xpath(xpath)
        data = selector.getall() if many else selector.get(default="")
        self.logger.debug(f"[{xpath=}] {selector=} {data=}")
        return data  # type: ignore[no-any-return]

    def match_data(self, data: str, pattern: str) -> str:
        regex = re.compile(pattern)
        if match := regex.search(data):
            return match.group(0)
        return ""

    def parse_ip_address(self, row: Selector) -> str:
        """IP address -> pattern matching 123.255.123.255"""
        ip = self.get_data(row, self.paths["ip"])
        return self.match_data(ip, r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

    def parse_port(self, row: Selector) -> int:
        """Port -> pattern matching 1-5 digits"""
        port = self.get_data(row, self.paths["port"])
        port_match = self.match_data(port, r"\d{1,5}")
        return int(port_match) if port_match else 0  # return 0 if no port is found

    def parse_protocol(self, row: Selector) -> str:
        """Protocol -> pattern matching http|https|socks4|socks5"""
        if not (proto_path := self.paths.get("protocol", "")):
            return ""
        protocol = self.get_data(row, proto_path)
        return self.match_data(protocol.lower(), r"http|https|socks4|socks5")

    def parse_country(self, row: Selector) -> str:
        """Country -> pattern matching 2 uppercase letters"""
        if not (country_path := self.paths.get("country", "")):
            return ""
        country = self.get_data(row, country_path)
        return self.match_data(country.upper(), r"[A-Z]{2}")

    def parse_anonymity(self, row: Selector) -> str:
        """Anonymity -> pattern matching anonymous|elite|transparent"""
        if not (anon_path := self.paths.get("anonymity", "")):
            return ""
        anonymity = self.get_data(row, anon_path)
        return self.match_data(anonymity.lower(), r"anonymous|elite|transparent")
