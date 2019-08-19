from config import *
from utilities import *

driver = ini_driver(gecko_driver, user_agent=user_agent, is_headless=headless)
driver.get(jumia_base_url)

#-close_popup
close_popup = driver.find_elements_by_css_selector(".-close_popup")
if len(close_popup) > 0:
    close_popup[0].click()

categories = ['electronics', 'phones-tablets','computing', 'playstation-games']

for category in categories:
    cat_url = f"{jumia_base_url}/{category}"
    driver.get(cat_url)
    for page in range(1,6):
        page_url = f"{cat_url}/?page={str(page)}"
        _ = get_url(page_url, driver)
        products = get_products(driver)