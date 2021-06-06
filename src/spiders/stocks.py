import re

import scrapy


class Stocks(scrapy.Spider):
    name = "stocks"

    def start_requests(self):
        for url in self.settings.get("URLS"):
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        company = response.xpath(
            '//a[@class="c-faceplate__company-link"]/text()'
        ).get()
        company = company.strip()

        price = response.xpath(
            '//span[@class="c-instrument c-instrument--last"]/text()'
        ).get()
        price = re.sub(r"\s", "", price)
        price = float(price)

        # Get "Consensus des analystes"
        blob = response.xpath(
            '//*[contains(text(), "Objectif de cours")]'
        ).get()
        if blob is None:
            target = "NA"
            potential = "NA"
        else:
            blob_cleaned = [x.strip() for x in blob.split("\n")]
            blob_cleaned = [x for x in blob_cleaned if not x.startswith("<")]
            target = float(re.sub(r"\s|EUR", "", blob_cleaned[1]))
            potential = float(re.sub(r"\s|%", "", blob_cleaned[3]))

        gauge = response.xpath(
            '//div[@class="c-median-gauge__tooltip"]/text()'
        ).get()
        if gauge is None:
            gauge = "NA"
        else:
            gauge = float(gauge)

        # Get "Variation sur 5 jours"
        blob = response.xpath(
            '//*[contains(text(), "Variation sur 5 jours")]'
        ).get()
        if blob is not None:
            blob_cleaned = [x.strip() for x in blob.split("\n")]
            blob_cleaned = [x for x in blob_cleaned if not x.startswith("<")]
            variation = float(re.sub(r"\s|%", "", blob_cleaned[3]))
        else:
            variation = "NA"

        # Store results
        result = {
            "company": company,
            "price": price,
            "target": target,
            "potential": potential,
            "gauge": gauge,
            "variation_5days": variation,
            "url": response.request.url,
        }
        return result
