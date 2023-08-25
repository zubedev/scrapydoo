from collections.abc import Generator
from typing import Any

import scrapy
from scrapy.http import Response

from scraper.items import ProxyItem


class ProxyScrapeSpider(scrapy.Spider):  # type: ignore
    name = "geonode"
    allowed_domains = ["geonode.com"]

    def start_requests(self) -> Generator[scrapy.Request, Any, None]:
        urls = [
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&anonymityLevel=elite&anonymityLevel=anonymous"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Generator[dict[str, Any], Any, None]:
        """
        {
            "data": [
                {
                    "_id": "630382e7e607212ee5f1e1c3",
                    "ip": "124.109.22.174",
                    "anonymityLevel": "elite",
                    "asn": "AS38527",
                    "city": "Pontianak",
                    "country": "ID",
                    "created_at": "2022-08-22T13:21:43.222Z",
                    "google": false,
                    "isp": "PT. JAWA POS NATIONAL NETWORK MEDIALINK",
                    "lastChecked": 1692956019,
                    "latency": 283.946,
                    "org": "",
                    "port": "5678",
                    "protocols": [
                    "socks4"
                    ],
                    "region": null,
                    "responseTime": 5008,
                    "speed": 1,
                    "updated_at": "2023-08-25T09:33:39.847Z",
                    "workingPercent": null,
                    "upTime": 93.06099608282037,
                    "upTimeSuccessCount": 3326,
                    "upTimeTryCount": 3574
                },
                ... ... ...
                ... ... ...
            ],
            "total": 5000,
            "limit": 500,
            "page": 1,
        }
        """
        # write the response to a file for debugging
        # Path("geonode.json").write_bytes(response.body)

        data = response.json()["data"]
        for d in data:
            yield ProxyItem(
                ip=d["ip"],
                port=int(d["port"]),
                protocol=d["protocols"][0],
                country=d["country"],
                anonymity=d["anonymityLevel"],
                source=self.name,
            )
