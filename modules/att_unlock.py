"""Use Safari to submit AT&T unlock request"""
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

print(f"Importing {os.path.basename(__file__)}...")


def send_keys_delay_random(controller, keys, min_delay=0.05, max_delay=0.25):
    for key in keys:
        controller.send_keys(key)
        time.sleep(random.uniform(min_delay, max_delay))


def unlock_att_device(imei):
    url = "https://www.att.com/deviceunlock/"
    browser = webdriver.Safari()
    browser.set_window_size(1200, 1024)
    browser.get(url)
    time.sleep(3)
    try:
        browser.find_element(By.XPATH, '//*[@id="fsrFocusFirst"]').click()
    except NoSuchElementException as _:
        print("No popup")
    finally:
        browser.find_element(By.CLASS_NAME, "unlockYourStatusLink").click()
        time.sleep(1.1)
        browser.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/label[2]/span/span[1]').click()
        time.sleep(2)
        send_keys_delay_random(browser.find_element(By.XPATH, '//*[@id="imeino"]'), "354442067957452")
        time.sleep(1)
        browser.find_element(By.XPATH, '//*[@id="agree"]').click()
        time.sleep(0.5)
        browser.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[3]/div/button[1]').click()
    time.sleep(40)


unlock_att_device(1)

# <a class="solo link-utility-secondary" tabindex="0" role="link" aria-label="Submit an unlock request">Submit an unlock request</a>
