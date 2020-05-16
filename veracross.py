from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select

import os
import json

import time

vc_link = "https://accounts.veracross.eu/asb/portals/login"
haiku_link = "https://asb.learning.powerschool.com/do/account/login"

def make_browser(headless=True):
    options = webdriver.ChromeOptions()
    if headless: options.add_argument("headless")
    b = webdriver.Chrome(options=options)
    b.implicitly_wait(5)
    return b

def vc_login(username, password, browser=None):
    if not browser: browser = make_browser(False)

    browser.find_element_by_id("username").send_keys(username)
    browser.find_element_by_id("password").send_keys(password)
    try:
        browser.find_element_by_id("recaptcha").click()
    except NoSuchElementException:
        browser.find_element_by_id("login-button").click()

def haiku_login(username, password, browser=None):
    if not browser: browser = make_browser(False)
    browser.find_element_by_id("parent_login").send_keys(username)
    browser.find_element_by_id("password").send_keys(password)
    browser.find_element_by_id("loginsubmit").click()

def get_class_json(username, password, browser=None):
    if not browser: browser = make_browser(False)
    vc_login(username, password, browser=browser)
    try:
        if browser.find_element_by_class_name("warning"):
            return False
    except NoSuchElementException:
        pass

    class_elements = browser.find_elements_by_class_name("class-status-active")
    classes = {}
    for c in class_elements:
        class_links = c.find_elements_by_tag_name("a")
        class_text = class_links[0].text
        class_code, class_name = class_text.split(": ")
        class_url = "/".join(class_links[1].get_attribute("href").split("/")[:-1])+"/students"
        classes[class_code] = {"name":class_name, "url":class_url}

    for code in classes:
        browser.get(classes[code]['url'])
        class_inner = browser.find_element_by_class_name("student-names-drop-down").get_attribute("innerHTML")
        class_json = json.loads(class_inner[class_inner.find("["):class_inner.rfind("]")+1].replace("=&gt;", ":").replace(":nil", ":null"))
        classes[code]["students"] = class_json
    return classes

def automate_dropdowns(username, password, link, browser=None, l=None):
    if not browser: browser = make_browser(False)
    browser.get(link)
    vc_login(username, password, browser)
    student_list = browser.find_elements_by_class_name("page-grade-form")[1]
    for student in student_list.find_elements_by_tag_name("li"):
        student.click()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-student-profile]")))
        dropdowns = browser.find_elements_by_tag_name("select")
        for i, dropdown in enumerate(dropdowns):
            dropdown = Select(dropdown)
            if isinstance(l, list) and i < len(l):
                try: dropdown.select_by_visible_text(l)
                except NoSuchElementException: print("Value not in the dropdown")
            else:
                try: dropdown.select_by_visible_text("ME")
                except NoSuchElementException: dropdown.select_by_visible_text("S")


def download_grades_from_haiku(username, password, link, browser=None):
    if not browser: browser = make_browser(False)
    browser.get(link)
    haiku_login(username, password, browser)

    if "accounts.google.com" in browser.current_url:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "identifierId"))).send_keys(username)
        browser.find_element_by_id("identifierNext").click()
        #by name since the id corresponds with enclosing div
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(password)
        browser.find_element_by_id("passwordNext").click()

    browser.get("https://asb.learning.powerschool.com/amitons/math7-2019-20allsections/grades_sbg")
    #not working?
    print(WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.TAG_NAME, "table"))))
    tables = browser.find_elements_by_tag_name("table")
    #table[0] seems to = student names, [2] = assignment names, [3] = grade data

    print(tables)



if __name__ == '__main__':
    download_grades_from_haiku("", "", haiku_link)
