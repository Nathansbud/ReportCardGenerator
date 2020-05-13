from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select

import os
import json

vc_link = "https://accounts.veracross.eu/asb/portals/login"

def make_browser(headless=True):
    options = webdriver.ChromeOptions()
    if headless: options.add_argument("headless")
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(3)
    return browser

def login(b, username, password):
    b.find_element_by_id("username").send_keys(username)
    b.find_element_by_id("password").send_keys(password)
    try:
        b.find_element_by_id("recaptcha").click()
    except NoSuchElementException:
        b.find_element_by_id("login-button").click()

def get_class_json(username, password, browser=make_browser(False)):
    login(browser, username, password)
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

def automate_dropdowns(browser, username, password, link, l=None):
    browser.get(link)
    login(browser, username, password)
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