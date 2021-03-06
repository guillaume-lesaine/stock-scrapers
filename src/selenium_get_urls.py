import argparse
import json
import logging
import os
import re
import sys

import backoff
import urllib3
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@backoff.on_exception(
    backoff.expo, urllib3.exceptions.MaxRetryError, max_tries=5, jitter=None
)
def selenium_connect(url, options):
    return webdriver.Remote(
        command_executor=url,
        desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
        options=options,
    )


def main(data: str, configuration: str):

    logging.info("Application 'selenium_get_urls' started.")
    logging.getLogger("urllib3").setLevel(logging.ERROR)

    # Initialize driver
    selenium_url = os.environ.get("SELENIUM_URL", default="localhost:4444")
    opts = Options()
    opts.headless = True
    try:
        driver = selenium_connect(
            f"http://{selenium_url}/wd/hub", options=opts
        )
        driver.set_page_load_timeout(10)
    except urllib3.exceptions.MaxRetryError:
        logging.error("Unable to connect to Selenium.")
        sys.exit(1)

    logging.info("Firefox driver is initialized.")

    # Go to site
    base_url = "https://www.boursorama.com/bourse/actions/palmares/france"
    driver.get(base_url)
    logging.info(f"Url '{base_url}' was successfully accessed.")

    # Pass cookie acknowledgment
    WebDriverWait(driver, 10,).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[@id="didomi-notice-agree-button"]'),
        )
    ).click()
    logging.info(f"Cookie acknowledgment was performed.")

    # Detect form and populate it
    form = driver.find_element_by_xpath('//form[@name="france_filter"]')

    with open(configuration) as f:
        configuration = json.loads(f.read())

    # Populate the dropdowns
    drop_down_divs = form.find_elements(
        By.XPATH,
        './/*[@class="c-select"]',
    )
    drop_down_selects = form.find_elements(
        By.XPATH,
        './/*[@class="c-select__select"]',
    )
    drop_down_names = [s.get_attribute("id") for s in drop_down_selects]

    for (div, name,) in zip(
        drop_down_divs,
        drop_down_names,
    ):
        div.click()
        options = div.find_elements(
            By.XPATH,
            './/*[contains(@class, "c-select__option is-selectable")]',
        )
        option = [o for o in options if o.text == configuration[name]][0]
        option.click()

    # Populate the tickboxes
    tick_box_labels = form.find_elements(
        By.XPATH,
        './/*[@class="c-input-checkbox__label"]',
    )
    tick_box_names = [l.get_attribute("for") for l in tick_box_labels]

    for (label, name,) in zip(
        tick_box_labels,
        tick_box_names,
    ):
        if configuration[name]:
            label.click()

    # Submit form
    submit = form.find_element_by_id("france_filter_filter")
    submit.click()

    logging.info(f"Form was submited.")

    # Go over each page to harvest the stock urls
    result = {}

    palmares = driver.find_element_by_xpath('//div[@class="c-palmares"]')

    # Get page urls
    # If more than 10 pages are displayed, the last page is found first, after
    # that pages are derived from 1 to n. If not the href of each page is
    # retrieved.
    try:
        last_page = palmares.find_element_by_xpath(
            './div[2]/div/a[@title="Derni??re page"]'
        )
        logging.info("More than 10 pages detected.")
        last_page_href = last_page.get_attribute("href")
        last_page_number = int(
            re.sub(
                fr"^{base_url}/page-(?P<page>\d*)\?.*",
                r"\g<page>",
                last_page_href,
            )
        )
        query = re.sub(fr"^{base_url}/page-\d*", "", last_page_href)
        page_hrefs = [
            f"{base_url}/page-{i}{query}"
            for i in range(1, last_page_number + 1)
        ]

    except NoSuchElementException:
        logging.info("Less than 10 pages detected.")
        pages = palmares.find_elements_by_xpath(
            './div[2]/div/a[contains(@href,"/actions/")]'
        )
        page_hrefs = [p.get_attribute("href") for p in pages]

    # For each page get all stock urls
    if len(page_hrefs) == 0:
        pass
    else:
        for p in page_hrefs:
            successful = False
            number_attempts = 0
            while not successful and number_attempts < 3:
                try:
                    number_attempts += 1
                    driver.get(p)
                    successful = True
                except TimeoutException:
                    logging.info("Refreshing page due to timeout ...")
                    driver.refresh()

            if successful:
                pass
            else:
                driver.get(p)

            palmares = driver.find_element_by_xpath(
                '//div[@class="c-palmares"]'
            )
            stocks = palmares.find_elements_by_xpath(
                './/*[contains(@href,"/cours/")]'
            )
            for s in stocks:
                result[s.text] = s.get_attribute("href")

            logging.info(
                f"Accessed '{driver.current_url}' "
                f"total stocks harvested: {len(result)}."
            )

    # Close driver
    driver.close()

    logging.info(
        "Urls have been harvested "
        + str(len(result))
        + " url(s) on "
        + str(len(page_hrefs))
        + " page(s)."
    )

    # Save urls to file
    path_urls = os.path.join(
        data,
        "urls.json",
    )

    if os.path.exists(path_urls):
        os.remove(path_urls)

    with open(
        path_urls,
        "w",
    ) as f:
        json.dump(
            result,
            f,
        )

    logging.info("Application 'selenium_get_urls' successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="Path to the data directory.")
    parser.add_argument(
        "--configuration", help="Path to the configuration file."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: %(levelname)s: %(message)s",
    )

    try:
        main(data=args.data, configuration=args.configuration)
    except Exception:
        logging.exception("Fatal error in main.", exc_info=True)
        raise
