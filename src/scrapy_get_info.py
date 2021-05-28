import argparse
import json
import os

from scrapy.crawler import CrawlerProcess
from spiders.stocks import Stocks


def main(data: str, logs: str):

    # Initialize logging path
    path_logs = os.path.join(logs, "scrapy.log")

    # Clean pre-existing output file
    path_info = os.path.join(data, "info.json")
    if os.path.exists(path_info):
        os.remove(path_info)

    # Read urls
    path_urls = os.path.join(data, "urls.json")
    with open(path_urls) as f:
        urls = list(json.loads(f.read()).values())

    # Crawl
    process = CrawlerProcess(
        settings={
            "LOG_FILE": path_logs,
            "FEED_URI": path_info,
            "FEED_FORMAT": "json",
            "FEED_EXPORTERS": {
                "json": "scrapy.exporters.JsonItemExporter",
            },
            "FEED_EXPORT_ENCODING": "utf-8",
            "URLS": urls,
        }
    )

    process.crawl(Stocks)
    process.start()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="Path to the data directory.")
    parser.add_argument("--logs", help="Path to the logs directory.")
    args = parser.parse_args()

    main(data=args.data, logs=args.logs)
