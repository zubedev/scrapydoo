import re
from collections.abc import Generator
from typing import Any

import scrapy
from scrapy import Selector
from scrapy.http import TextResponse

from scraper.items import ProxyItem


class ProxyNovaSpider(scrapy.Spider):  # type: ignore
    name = "proxynova"
    allowed_domains = ["proxynova.com"]

    def start_requests(self) -> Generator[scrapy.Request, Any, None]:
        urls = ["https://www.proxynova.com/proxy-server-list/elite-proxies/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"playwright": True})

    def parse(self, response: TextResponse, **kwargs: Any) -> Generator[dict[str, Any], Any, None]:
        # write the response to a file for debugging
        # Path("proxynova.html").write_bytes(response.body)

        rows = response.xpath("//table[@id='tbl_proxy_list']/tbody/tr")
        for r in rows:
            yield ProxyItem(
                ip=self.parse_ip_address(r),
                port=self.parse_port(r),
                protocol="https",
                country=self.parse_country(r),
                anonymity="elite",
                source=self.name,
            )

    def parse_ip_address(self, sel: Selector) -> str:
        """
        - IP address table column with <abbr> tag

            <td align="left" title="...">
                <abbr title="...">
                    <script>...</script>111.222.111.222
                </abbr>
            </td>

        - IP address table column without <abbr> tag

            <td align="left" title="...">
                <script>...</script>111.222.111.222
            </td>
        """
        pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")

        if sel.xpath("./td[1]/abbr"):  # if there is an <abbr> tag
            self.logger.debug(f"[Selector=`./td[1]/abbr/text()`] {sel.xpath('./td[1]/abbr/text()')}")
            ip_selector = sel.xpath("./td[1]/abbr/text()")
        else:  # if there is no <abbr> tag
            self.logger.debug(f"[Selector=`./td[1]/text()`] {sel.xpath('./td[1]/text()')}")
            ip_selector = sel.xpath("./td[1]/text()")

        ip = ip_selector[-1].get() if len(ip_selector) > 1 else ip_selector.get()
        # remove the newline character and any leading or trailing whitespace
        # return ip.replace("\n", "").strip()
        if ip := pattern.search(ip):
            return ip.group(1)
        return ""  # return empty string if no IP address is found

    def parse_port(self, sel: Selector) -> int:
        """
        - Port table column with <a> tag

            <td align="left">
                <a href="..." title="...">1080</a>
            </td>

        - Port table column without <a> tag

            <td align="left">
                8443
            </td>
        """
        if sel.xpath("./td[2]/a"):  # if there is an <a> tag
            self.logger.debug(f"[Selector=`./td[2]/a/text()`] {sel.xpath('./td[2]/a/text()')}")
            port = sel.xpath("./td[2]/a/text()").get()
        else:  # if there is no <a> tag
            self.logger.debug(f"[Selector=`./td[2]/text()`] {sel.xpath('./td[2]/text()')}")
            port = sel.xpath("./td[2]/text()").get()
        # remove the newline character and any leading or trailing whitespace
        return int(port.replace("\n", "").strip())

    def parse_country(self, sel: Selector) -> str:
        """
        - Country code with <img> tag `alt` attribute

            <td align="left">
                <img src="..." alt="au" class="..." />
                <a href="/proxy-server-list/country-au" title="...">Australia</a>
            </td>
        """
        self.logger.debug("[Selector=`./td[6]/img/@alt`]")
        return str(sel.xpath("./td[6]/img/@alt").get()).upper()
