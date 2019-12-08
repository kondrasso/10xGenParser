import os
import pandas as pd
from time import sleep
from selenium import common
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


def parse_data(drv, filename, to_csv=True):
    # going to the table page and selecting number of rows
    drv.get(os.path.join(os.getcwd(), filename))
    drv.find_element_by_id('main-page-tab-tab-analysis').click()
    Select(drv.find_element_by_xpath('//select[@aria-label="rows per page"]')).select_by_value('100')
    drv.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # getting column names
    headers = [_.text for _ in drv.find_elements_by_xpath('//*[contains(@class, '
                                                          '"rt-th rt-resizable-header -cursor-pointer")]')]
    data = []

    # cycling through pages and grabbing raw data
    can_click_next = True
    while can_click_next:
        sleep(1)
        table = drv.find_element_by_xpath('//*[contains(@class, "rt-tbody")]')
        for _ in table.find_elements_by_xpath('//*[contains(@class, "rt-tr-group")]'):
            data.append(_.text)
        try:
            WebDriverWait(drv, 5).until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".-next .-btn")))
            drv.find_element_by_css_selector(".-next .-btn").click()
        except common.exceptions.TimeoutException:
            can_click_next = False
    # pandas
    df = pd.DataFrame(map(lambda x: x.split('\n'), data), columns=headers).dropna()
    if to_csv:
        df.to_csv('{}.csv'.format(filename.split('.')[0]))
    return df


def create_driver():
    # creating webdriver instance
    options = Options()
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options, executable_path=os.path.join(os.getcwd(), 'chromedriver.exe'))
    return driver


def main():
    print('Specify file name: ')
    file = input()
    parse_data(create_driver(), file)


if __name__ == '__main__':
    main()
