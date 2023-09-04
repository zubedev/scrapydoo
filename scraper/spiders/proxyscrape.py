from collections.abc import Generator
from typing import Any

from scrapy.http import TextResponse

from scraper.base import BaseSpider
from scraper.items import ProxyItem
from scraper.types import ElementPathsTypedDict


class ProxyScrapeSpider(BaseSpider):
    """https://docs.proxyscrape.com

    in plain text format:
        111.21.183.58:9091
        78.38.93.20:3128
        103.45.105.226:8080
        ... ... ...
    """

    name = "proxyscrape"
    allowed_domains = ["proxyscrape.com"]

    def __init__(self, name: str = None, **kwargs: Any) -> None:  # type: ignore[assignment]
        super().__init__(name=name, **kwargs)
        self.start_urls: list[str] = self.build_urls()

    def build_urls(self) -> list[str]:
        protocols = ["http", "socks4", "socks5"]
        ssl = ["yes", "no"]
        anonymity = ["elite", "anonymous"]

        return [
            (
                f"https://api.proxyscrape.com/v2/?request=displayproxies&"
                f"protocol={p}&ssl={s}&anonymity={a}&country=all&timeout=10000"
            )
            for a in anonymity
            for s in ssl
            for p in protocols
        ]

    def set_element_paths(self) -> ElementPathsTypedDict:
        return {}  # type: ignore[typeddict-item]

    def parse(self, response: TextResponse, **kwargs: Any) -> Generator[dict[str, Any], Any, None]:
        url = response.url
        params = url.split("&")[1:]

        protocol = params[0].split("=")[1]
        ssl = params[1].split("=")[1]
        anonymity = params[2].split("=")[1]

        if protocol == "http" and ssl == "yes":
            protocol = "https"

        for line in response.text.splitlines():
            ip, port = line.split(":")
            ip = self.match_data(ip, self.get_pattern("ip"))
            port = self.match_data(port, self.get_pattern("port"))
            yield ProxyItem(
                ip=ip,
                port=int(port) if port else 0,
                protocol=protocol,
                country="",  # not available
                anonymity=anonymity,
                source=self.name,
            )
