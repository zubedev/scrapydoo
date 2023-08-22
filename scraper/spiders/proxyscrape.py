import re
from collections.abc import Generator
from typing import Any

import scrapy
from scrapy import Selector
from scrapy.http import TextResponse

from scraper.items import ProxyItem


class ProxyScrapeSpider(scrapy.Spider):  # type: ignore
    name = "proxyscrape"
    allowed_domains = ["proxyscrape.com"]

    def start_requests(self) -> Generator[scrapy.Request, Any, None]:
        urls = ["https://proxyscrape.com/free-proxy-list/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"playwright": True})

    def parse(self, response: TextResponse, **kwargs: Any) -> Generator[dict[str, Any], Any, None]:
        """
        <tbody id="proxytable">
            <tr>
                <td>36.112.137.173</td>
                <td>8888</td>
                <td>HTTP</td>
                <td>China</td>
                <td>Anonymous</td>
                <td class="ms-section">7651ms</td>
                <td>44.4%</td>
                <td>8 minutes</td>
            </tr>
            ... ... ...
        </tbody>
        """
        # write the response to a file for debugging
        # Path("proxyscrape.html").write_bytes(response.body)

        rows = response.xpath("//tbody[@id='proxytable']/tr")
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
        <tr>
            <td>36.112.137.173</td>
            ... ... ...
        </tr>
        """
        selector = "./td[1]/text()"
        ip_selector = row.xpath(selector)
        ip = ip_selector.get()
        self.logger.debug(f"[{selector=}] {ip_selector=} {ip=}")

        pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if match := pattern.search(ip):
            return match.group(0)
        return ""  # return empty string if no IP address is found

    def parse_port(self, row: Selector) -> int:
        """Port -> 2nd table column
        <tr>
            ... ... ...
            <td>8888</td>
            ... ... ...
        </tr>
        """
        selector = "./td[2]/text()"
        port_sel = row.xpath(selector)
        port = port_sel.get()
        self.logger.debug(f"[{selector=}] {port_sel=} {port=}")

        pattern = re.compile(r"\d{1,5}")
        if match := pattern.search(port):
            return int(match.group(0))
        return 0  # return 0 if no port is found

    def parse_protocol(self, row: Selector) -> str:
        """Protocol -> 3rd table column
        <tr>
            ... ... ...
            <td>HTTP</td>
            ... ... ...
        </tr>
        """
        selector = "./td[3]/text()"
        protocol_sel = row.xpath(selector)
        protocol = str(protocol_sel.get()).lower()
        self.logger.debug(f"[{selector=}] {protocol_sel=} {protocol=}")

        pattern = re.compile(r"http|https|socks4|socks5")
        if match := pattern.search(protocol):
            return match.group(0)
        return ""  # return empty string if no protocol is found

    def parse_country(self, row: Selector) -> str:
        """Country -> 4th table column
        <tr>
            ... ... ...
            <td>United States</td>
            ... ... ...
        </tr>
        """
        selector = "./td[4]/text()"
        country_sel = row.xpath(selector)
        country = str(country_sel.get()).lower()
        self.logger.debug(f"[{selector=}] {country_sel=} {country=}")

        pattern = re.compile(r"[a-z ]+")
        if match := pattern.search(country):
            return match.group(0)
        return ""  # return empty string if no country is found

    def parse_anonymity(self, row: Selector) -> str:
        """Anonymity -> 5th table column
        <tr>
            ... ... ...
            <td>Anonymous</td>
            ... ... ...
        </tr>
        """
        selector = "./td[5]/text()"
        anonymity_sel = row.xpath(selector)
        anonymity = str(anonymity_sel.get()).lower()
        self.logger.debug(f"[{selector=}] {anonymity_sel=} {anonymity=}")

        pattern = re.compile(r"anonymous|elite|transparent")
        if match := pattern.search(anonymity):
            return match.group(0)
        return ""  # return empty string if no protocol is found
