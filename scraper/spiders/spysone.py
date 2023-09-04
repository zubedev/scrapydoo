from collections.abc import Callable, Generator
from typing import Any

import scrapy
from scrapy import Selector
from scrapy.http import TextResponse
from scrapy.selector import SelectorList

from scraper.base import BaseSpider
from scraper.types import ElementPathsTypedDict


class ProxyScrapeSpider(BaseSpider):
    """
    <tbody>
        <tr>
            <td colspan="4"><h1>Free anonymous proxy list. High anonymous proxies. ANM &amp; HIA list.</h1></td>
            <form method="post" action="/en/anonymous-proxy-list/"></form>
            <td align="right" colspan="5">
                <input type="hidden" name="xx0" value="597a786904c5603a4d7954dfdb397baf">
                ... ... ...
            </td>
        </tr>
        <tr class="spy1x">...</tr>
        <tr class="spy1xx" onmouseover="..." onmouseout="..." style="...">
            <td colspan="1"><font class="spy14">31.220.55.59<script ...>...</script>...80</font></td>
            <td colspan="1"><a href="/en/http-proxy-list/"><font class="spy1">HTTPS</font></a></td>
            <td colspan="1"><a href="/en/anonymous-proxy-list/"><font class="spy1">HIA</font></a></td>
            <td colspan="1"><a href="/free-proxy-list/US/">...</td>
            <td colspan="1"><font class="spy1">31.220.55.59</font> <font class="spy14">...</font></td>
            <td colspan="1">...</td>
            ... ... ...
        </tr>
        <tr class="spy1x" onmouseover="..." onmouseout="..." style="...">
            <td colspan="1"><font class="spy14">162.240.75.37<script ...>...</script>...80</font></td>
            <td colspan="1"><a href="/en/http-proxy-list/"><font class="spy1">HTTP</font></a></td>
            <td colspan="1"><a href="/en/anonymous-proxy-list/"><font class="spy1">ANM</font></a></td>
            <td colspan="1"><a href="/free-proxy-list/US/"><font class="spy14">United States</font></a></td>
            <td colspan="1">...</td>
            ... ... ...
        </tr>
        ... ... ...
        ... ... ...
    </tbody>
    """

    name = "spysone"
    allowed_domains = ["spys.one"]
    start_urls = ["https://spys.one/en/anonymous-proxy-list/"]
    use_flaresolverr = True
    use_playwright = True

    def get_callback(self) -> tuple[Callable, dict[str, Any] | None]:  # type: ignore[type-arg]
        return self.prepare, {"cookies": self.cookies, "headers": self.headers, "meta": self.meta}

    def prepare(self, response: TextResponse, **kwargs: Any) -> Generator[scrapy.Request, Any, None]:
        # get the value from the input field with name="xx0"
        xx0 = response.xpath("//input[@name='xx0']/@value").get()
        formdata = {"xx0": xx0, "xpp": "5", "xf1": "1", "xf2": "0", "xf4": "0", "xf5": "0"}
        yield scrapy.FormRequest.from_response(
            response,
            formdata=formdata,
            method="POST",
            callback=self.parse,
            **kwargs,  # cookies, headers and meta
        )

    def set_element_paths(self) -> ElementPathsTypedDict:
        return {
            "rows": "//tr[@class='spy1x' or @class='spy1xx']",
            "ip": "./td[1]/font/text()",
            "port": "./td[1]/font/text()",
            "protocol": "./td[2]/a/font/text()",
            "country": "./td[4]/a/@href",
            "anonymity": "./td[3]/a/font/text()",
        }

    def get_rows(self, response: TextResponse, xpath: str | None = None) -> SelectorList[Selector]:
        return response.xpath(xpath or self.paths["rows"])[1:]  # drop the first row

    def parse_port(self, row: Selector) -> int:
        port = self.get_data(row, self.paths["port"], many=True)[-1]  # get the last element
        port_match = self.match_data(port, r"\d{1,5}")
        return int(port_match) if port_match else 0  # return 0 if no port is found

    def parse_protocol(self, row: Selector) -> str:
        proto: list[str] = self.get_data(row, self.paths["protocol"], many=True)
        protocol = str("".join(proto)).lower()
        return self.match_data(protocol, r"http|https|socks4|socks5")

    def parse_anonymity(self, row: Selector) -> str:
        anonymity = self.get_data(row, self.paths["anonymity"])
        mapping = {"anm": "anonymous", "hia": "elite", "noa": "transparent"}
        data = self.match_data(anonymity.lower(), r"anm|hia|noa")
        return mapping[data] if data else ""
