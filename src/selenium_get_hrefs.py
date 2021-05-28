import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Firefox()

driver.get("https://www.boursorama.com/bourse/actions/palmares/france")

WebDriverWait(driver, 10,).until(
    EC.element_to_be_clickable(
        By.XPATH,
        '//button[@id="didomi-notice-agree-button"]',
    )
).click()

form = driver.find_element_by_xpath('//form[@name="france_filter"]')

drop_down_divs = form.find_elements(
    By.XPATH,
    './/*[@class="c-select"]',
)
drop_down_selects = form.find_elements(
    By.XPATH,
    './/*[@class="c-select__select"]',
)
drop_down_names = [s.get_attribute("id") for s in drop_down_selects]

tick_box_divs = form.find_elements(
    By.XPATH,
    './/*[@class="c-input-checkbox__label"]',
)
tick_box_labels = form.find_elements(
    By.XPATH,
    './/*[@class="c-input-checkbox__label"]',
)
tick_box_names = [l.get_attribute("for") for l in tick_box_labels]

configuration = {
    "france_filter_market": "Indice CAC 40",
    "france_filter_sector": "Tous les secteurs",
    "france_filter_variation": "Palmarès",
    "france_filter_period": "Depuis",
    "france_filter_peaEligibility": True,
    "france_filter_peaPmeEligibility": False,
}

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

for (label, name,) in zip(
    tick_box_labels,
    tick_box_names,
):
    if configuration[name]:
        label.click()

submit = form.find_element_by_id("france_filter_filter")
submit.click()

# Get palmares step by step
result = {}

palmares = driver.find_element_by_xpath('//div[@class="c-palmares"]')
pages = palmares.find_elements_by_xpath(
    './div[2]/div/a[contains(@href,"/actions/")]'
)
page_hrefs = [p.get_attribute("href") for p in pages]

if len(page_hrefs) == 0:
    pass
else:
    for p in page_hrefs:
        driver.get(p)
        palmares = driver.find_element_by_xpath('//div[@class="c-palmares"]')
        stocks = palmares.find_elements_by_xpath(
            './/*[contains(@href,"/cours/")]'
        )

        for s in stocks:
            result[s.text] = s.get_attribute("href")

hrefs_path = os.path.join(
    "data",
    "hrefs.json",
)
with open(
    hrefs_path,
    "w",
) as f:
    json.dump(
        result,
        f,
    )
