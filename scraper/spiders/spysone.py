import re
from collections.abc import Generator
from typing import Any

import scrapy
from scrapy import Selector
from scrapy.http import TextResponse

from scraper.items import ProxyItem


class ProxyScrapeSpider(scrapy.Spider):  # type: ignore
    name = "spysone"
    allowed_domains = ["spys.one"]

    def start_requests(self) -> Generator[scrapy.Request, Any, None]:
        url = "https://spys.one/en/anonymous-proxy-list/"
        # do a get request to get the form data for the post request
        yield scrapy.Request(url=url, callback=self.prepare, meta={"playwright": True})

    def prepare(self, response: TextResponse, **kwargs: Any) -> Generator[scrapy.Request, Any, None]:
        # get the value from the input field with name="xx0"
        xx0 = response.xpath("//input[@name='xx0']/@value").get()
        formdata = {"xx0": xx0, "xpp": "5", "xf1": "1", "xf2": "0", "xf4": "0", "xf5": "0"}
        yield scrapy.FormRequest.from_response(
            response, formdata=formdata, method="POST", callback=self.parse, meta={"playwright": True}
        )

    def parse(self, response: TextResponse, **kwargs: Any) -> Generator[dict[str, Any], Any, None]:
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
        # write the response to a file for debugging
        # Path(f"{self.name}.html").write_bytes(response.body)

        # get the rows by combining the two selectors with class="spy1x" and class="spy1xx" but drop the first row
        rows = response.xpath("//tr[@class='spy1x' or @class='spy1xx']")[1:]
        for r in rows:
            yield ProxyItem(
                ip=self.parse_ip_address(r),
                port=self.parse_port(r),
                protocol=self.parse_protocol(r),
                country=self.parse_country(r),
                anonymity=self.parse_anonymity(r),
                source=self.name,
            )

    def parse_ip_address(self, row: Selector) -> str:
        """IP address -> 1st table column
        <tr class="spy1xx" onmouseover="..." onmouseout="..." style="...">
            <td colspan="1"><font class="spy14">31.220.55.59<script ...>...</script>...80</font></td>
            ... ... ...
        </tr>
        """
        selector = "./td[1]/font/text()"
        ip_selector = row.xpath(selector)
        ip = ip_selector.getall()[0]  # get the first element
        self.logger.debug(f"[{selector=}] {ip_selector=} {ip=}")

        pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if match := pattern.search(ip):
            return match.group(0)
        return ""  # return empty string if no IP address is found

    def parse_port(self, row: Selector) -> int:
        """Port -> 1st table column
        <tr class="spy1x" onmouseover="..." onmouseout="..." style="...">
            <td colspan="1"><font class="spy14">162.240.75.37<script ...>...</script>...80</font></td>
            ... ... ...
        </tr>
        """
        selector = "./td[1]/font/text()"
        port_sel = row.xpath(selector)
        port = port_sel.getall()[-1]  # get the last element
        self.logger.debug(f"[{selector=}] {port_sel=} {port=}")

        pattern = re.compile(r"\d{1,5}")
        if match := pattern.search(port):
            return int(match.group(0))
        return 0  # return 0 if no port is found

    def parse_protocol(self, row: Selector) -> str:
        """Protocol -> 2nd table column
        <tr>
            ... ... ...
            <td colspan="1"><a href="/en/http-proxy-list/"><font class="spy1">HTTP</font></a></td>
            ... ... ...
        </tr>
        """
        selector = "./td[2]/a/font/text()"
        protocol_sel = row.xpath(selector)
        protocol = str("".join(protocol_sel.getall())).lower()
        self.logger.debug(f"[{selector=}] {protocol_sel=} {protocol=}")

        pattern = re.compile(r"http|https|socks4|socks5")
        if match := pattern.search(protocol):
            return match.group(0)
        return ""  # return empty string if no protocol is found

    def parse_country(self, row: Selector) -> str:
        """Country -> 4th table column
        <tr>
            ... ... ...
            <td colspan="1"><a href="/free-proxy-list/US/">...</td>
            ... ... ...
        </tr>
        """
        selector = "./td[4]/a/@href"
        country_sel = row.xpath(selector)
        country = country_sel.get()
        self.logger.debug(f"[{selector=}] {country_sel=} {country=}")

        pattern = re.compile(r"[A-Z]{2}")
        if match := pattern.search(country):
            return match.group(0)
        return ""  # return empty string if no country is found

    def parse_anonymity(self, row: Selector) -> str:
        """Anonymity -> 3rd table column
        <tr>
            ... ... ...
            <td colspan="1"><a href="/en/anonymous-proxy-list/"><font class="spy1">ANM</font></a></td>
            ... ... ...
        </tr>
        """
        selector = "./td[3]/a/font/text()"
        anonymity_sel = row.xpath(selector)
        anonymity = str(anonymity_sel.get()).lower()
        self.logger.debug(f"[{selector=}] {anonymity_sel=} {anonymity=}")

        mapping = {"anm": "anonymous", "hia": "elite", "noa": "transparent"}

        pattern = re.compile(r"anm|hia|noa")
        if match := pattern.search(anonymity):
            return mapping.get(match.group(0), "")
        return ""  # return empty string if no protocol is found
