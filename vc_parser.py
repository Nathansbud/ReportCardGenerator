from selenium import webdriver
import os
import json

with open(os.path.join(os.path.dirname(__file__), "credentials", "veracross.json"), "r+") as jf: veracross = json.load(jf)
def get_classes(vc_link="https://accounts.veracross.eu/asb/portals/login"):
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
        students = browser.find_elements_by_class_name("full_name")
        if len(students) >= 2:
            students = students[1:-1]
            #split on triple space (sep of name & grade), split on comma & reverse to have First Last be name structure
            student_names = [" ".join(student.text.split("   ")[0].split(", ")[::-1]) for student in students]
            classes[code]['students'] = student_names
        else:
            pass
    return classes
if __name__ == "__main__":
    print(get_classes())
    pass