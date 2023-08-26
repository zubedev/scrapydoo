from scraper.base import BaseSpider
from scraper.types import ElementPathsTypedDict


class ProxyScrapeSpider(BaseSpider):
    """
    <tbody
        <tr>
            <td ...><span ...>47.112.157.97</span></td>
            <td ...><span ...>8060</span></td>
            <td ...><div ...><span><svg ...>...</svg></span><span class="uppercase">CN</span></div></td>
            <td ...><div ...><span class="... uppercase">socks5</span></div></td>
            <td ...><div ...>elite (HIA)</div></td>
            <td ...><div ...>...</div></td>
            ... ... ...
        </tr>
        ... ... ...
        ... ... ...
    </tbody>
    """

    name = "geonode"
    allowed_domains = ["geonode.com"]
    start_urls = ["https://geonode.com/free-proxy-list"]
    use_playwright = True

    def set_element_paths(self) -> ElementPathsTypedDict:
        return {
            "rows": "//tbody/tr",
            "ip": "./td[1]/span/text()",
            "port": "./td[2]/span/text()",
            "protocol": "./td[4]/div/span/text()",
            "country": "./td[3]/div/span[@class='uppercase']/text()",
            "anonymity": "./td[5]/div/text()",
        }
