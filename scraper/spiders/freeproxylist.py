from scrapy import Selector

from scraper.base import BaseSpider
from scraper.types import ElementPathsTypedDict


class ProxyScrapeSpider(BaseSpider):
    """
    <tbody>
        <tr>
            <td>185.178.47.135</td>
            <td>80</td>
            <td>RU</td>
            <td class="hm">Russian Federation</td>
            <td>elite proxy</td>
            <td class="hm">yes</td>
            <td class="hx">no</td>
            <td class="hm">22 secs ago</td>
        </tr>
    </tbody>
    """

    name = "freeproxylist"
    allowed_domains = ["free-proxy-list.net"]
    start_urls = ["https://free-proxy-list.net/"]
    use_playwright = False

    def set_element_paths(self) -> ElementPathsTypedDict:
        return {
            "rows": "//section[@id='list']//table/tbody/tr",
            "ip": "./td[1]/text()",
            "port": "./td[2]/text()",
            "protocol": "./td[7]/text()",
            "country": "./td[3]/text()",
            "anonymity": "./td[5]/text()",
        }

    def parse_protocol(self, row: Selector) -> str:
        protocol = self.get_data(row, self.paths["protocol"])
        data = self.match_data(protocol.lower(), r"yes|no")
        return "https" if data == "yes" else "http"
