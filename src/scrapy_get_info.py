import argparse
import json
import logging
import os

from scrapy.crawler import CrawlerProcess
from spiders.stocks import Stocks


def main(data: str):

    logging.info("Application 'scrapy_get_info' started.")

    # Clean pre-existing output file
    path_info = os.path.join(data, "info.json")
    if os.path.exists(path_info):
        os.remove(path_info)

    # Read urls
    path_urls = os.path.join(data, "urls.json")
    with open(path_urls) as f:
        urls = list(json.loads(f.read()).values())
    logging.info(f"Urls loaded for {len(urls)} stocks.")

    # Crawl
    process = CrawlerProcess(
        settings={
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

    logging.info("Application 'scrapy_get_info' terminated successfully.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="Path to the data directory.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: %(levelname)s: %(message)s",
    )

    try:
        main(data=args.data)
    except Exception:
        logging.exception("Fatal error in main.", exc_info=True)
        raise
