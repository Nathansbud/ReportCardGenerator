from selenium import webdriver
import os
import json

with open(os.path.join(os.path.dirname(__file__), "credentials", "veracross.json"), "r+") as jf: veracross = json.load(jf)
def get_class_json(vc_link="https://accounts.veracross.eu/asb/portals/login"):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    browser = webdriver.Chrome(options=options)

    browser.get(vc_link)
    #Login
    browser.find_element_by_id("username").send_keys(veracross['username'])
    browser.find_element_by_id("password").send_keys(veracross['password'])
    browser.find_element_by_id("recaptcha").click()
    browser.implicitly_wait(10)
    #Get Classes
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
if __name__ == "__main__":
    print(get_class_json())
    pass