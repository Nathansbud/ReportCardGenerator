from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

import atexit
import json
import os

report_login_page = "https://accounts.veracross.eu/asb/portals/login"
login_path = os.path.join(os.path.dirname(__file__), "credentials", "login.json")

with open(login_path) as lf:
    login = json.load(lf)


def make_chrome_browser(run_headless=False, quit_on_done=False):
    options = webdriver.ChromeOptions()
    if run_headless: options.add_argument("headless")
    b = webdriver.Chrome(options=options)
    b.implicitly_wait(2)
    WebDriverWait(b, 10)
    if quit_on_done: atexit.register(b.close)
    return b

browser = make_chrome_browser()


def veracross_login():
    global browser

    browser.get(report_login_page)
    username_field = browser.find_element_by_id('username')
    password_field = browser.find_element_by_id('password')
    login_button = browser.find_element_by_id('recaptcha')

    username_field.send_keys(login['username'])
    password_field.send_keys(login['password'])
    login_button.click()

def get_class_links():
    global browser

    gradebook_class = "class-link"
    report_ending = "report-cards"
    links = []
    for elem in browser.find_elements_by_class_name(gradebook_class):
        link = elem.get_attribute('href')
        link_split = link.split("/")
        link_split[-1] = report_ending #Replace "gradebook" with "report-cards", where students are
        links.append("/".join(link_split))
    return links

def open_students():
    global browser

    student_class = "students"
    student_list = browser.find_elements_by_class_name(student_class)[0] #Get sidebar of student elems
    student_elems = student_list.find_elements_by_tag_name('li') #Get all students
    student_select = "Paranjaay Mahtani"
    for student in student_elems:
        if student.get_attribute("textContent") == student_select:
            student.click()

if __name__ == '__main__':
    veracross_login()
    gradebooks = get_class_links()
    browser.get(gradebooks[0])
    open_students()


