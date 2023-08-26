from scrapy import Selector

from scraper.base import BaseSpider
from scraper.types import ElementPathsTypedDict


class ProxyScrapeSpider(BaseSpider):
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

    name = "proxyscrape"
    allowed_domains = ["proxyscrape.com"]
    start_urls = ["https://proxyscrape.com/free-proxy-list/"]
    use_playwright = True

    def set_element_paths(self) -> ElementPathsTypedDict:
        return {
            "rows": "//tbody[@id='proxytable']/tr",
            "ip": "./td[1]/text()",
            "port": "./td[2]/text()",
            "protocol": "./td[3]/text()",
            "country": "./td[4]/text()",
            "anonymity": "./td[5]/text()",
        }

    def parse_country(self, row: Selector) -> str:
        country = self.get_data(row, self.paths["country"])
        return self.match_data(country.lower(), r"[a-z ]+")
