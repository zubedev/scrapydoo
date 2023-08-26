from scrapy import Selector

from scraper.base import BaseSpider
from scraper.types import ElementPathsTypedDict


class ProxyNovaSpider(BaseSpider):
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

    - Port table column with <a> tag

        <td align="left">
            <a href="..." title="...">1080</a>
        </td>

    - Port table column without <a> tag

        <td align="left">
            8443
        </td>

    - Country code with <img> tag `alt` attribute

        <td align="left">
            <img src="..." alt="au" class="..." />
            <a href="/proxy-server-list/country-au" title="...">Australia</a>
        </td>
    """

    name = "proxynova"
    allowed_domains = ["proxynova.com"]
    start_urls = ["https://www.proxynova.com/proxy-server-list/elite-proxies/"]
    use_playwright = True

    def set_element_paths(self) -> ElementPathsTypedDict:
        return {
            "rows": "//table[@id='tbl_proxy_list']/tbody/tr",
            "ip": "./td[1]/abbr/text()",
            "port": "./td[2]/a/text()",
            "protocol": "",  # not available
            "country": "./td[6]/img/@alt",
            "anonymity": "",  # not available
        }

    def parse_ip_address(self, row: Selector) -> str:
        if row.xpath("./td[1]/abbr"):  # if there is an <abbr> tag
            ip_list = self.get_data(row, "./td[1]/abbr/text()", many=True)
        else:  # if there is no <abbr> tag
            ip_list = self.get_data(row, "./td[1]/text()", many=True)
        ip = ip_list[-1] if len(ip_list) > 1 else ip_list[0]
        return self.match_data(ip, r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

    def parse_port(self, row: Selector) -> int:
        if row.xpath("./td[2]/a"):  # if there is an <a> tag
            port = self.get_data(row, self.paths["port"])
        else:  # if there is no <a> tag
            port = self.get_data(row, "./td[2]/text()")
        port_match = self.match_data(port, r"\d{1,5}")
        return int(port_match) if port_match else 0  # return 0 if no port is found

    def parse_protocol(self, row: Selector) -> str:
        return "https"  # default to https

    def parse_anonymity(self, row: Selector) -> str:
        return "elite"  # default to elite
