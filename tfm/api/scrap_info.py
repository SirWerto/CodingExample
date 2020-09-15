import requests
import re
import json
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
from datetime import date, timedelta
from time import sleep

### BASIC INFO ########################################################################


def get_info(server):

    login_html = server["url"] + "/login.php"
    try:
        r = requests.get(login_html, timeout=5)
        r.raise_for_status()

    except ConnectionError as e:
        raise BasicRequestError(e, "Unable to connect") #Acabar
        raise

    except RequestException as e:
        raise BasicRequestError(e, "Request error") #Acabar
        raise
    else:
        return parse_server_info(r.text, server)


def parse_server_info(req, server):

    #Beauti
    rs = BeautifulSoup(req, 'html.parser')

    #Size parsing
    try:
        info_size = rs.find_all('script')[9]
        f_flags = rs.find_all("script")[-1].text.splitlines()[1][26:-1]

    except Exception as e:
        raise ParseBasicError(e, "Failed while basic parse")
        raise

    else:
        line = info_size.string.splitlines()[2]
        line = line.split("{")[3].split(",")[:-1]
        line[5] = line[5][:-3] 

        size = {}
        for x in line:
            key, value = x.split(":")
            key = key[1:-1]
            size[key] = int(value)

    #Parsing
    regex = re.compile('Travian\.Game.*')
    fields = re.findall(regex, req)

    #Dict
    server['title'] = rs.title.text.replace("Travian ", "").upper()
    server['version'] = fields[0].split("'")[1]
    server['worldId'] = fields[1].split("'")[1]
    server['speed'] = fields[2].split("=")[1][1:-1]
    server['language'] = fields[4].split('"')[1]
    server['size'] = size
    server['game_flags'] = json.loads(f_flags)

    return 


### DAYS INFO ########################################################################

def get_day(server):

    gecko_path = "/home/jorge/tfm-jvm/pruebas/geckodriver"
    driver = start_browser(gecko_path)
    driver.get(server["url_reference"] + "#login")
    sleep(5)

    server_list = driver.find_element_by_class_name('worldGroup').text.splitlines()
    driver.quit()

    server["start_day"] = extract_day(server_list, server["title"])

    if server["start_day"] == None:
        raise ParseDayError("Bad Parse Day")

def extract_day(server_list, title):

    for i in range(0,len(server_list),2):
        if server_list[i] == title:
            temp = int(server_list[i+1].split()[0])
            diftemp = timedelta(days=temp)
            temp = date.today() - diftemp
            return temp.strftime("%d/%m/%Y")

    

def start_browser(gecko_path):
    
    options = Options()
    options.headless = True

    try:
        my_driver = webdriver.Firefox(options=options, executable_path=gecko_path)
    except WebDriverException as e:
        raise SeleniumError(e, "Can't initializate the browser")
    else:
        return my_driver



### Get all Info

def scraps(server):

    get_info(server)
    get_day(server)

    server["_id"] = str(server["start_day"]) + str(server["url"])
    
###ERROR

class ServerInfoError(Exception):
    """Base class for errors while parsing the map"""
    pass

class BasicRequestError(ServerInfoError):
    """Bad requests on basic info"""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class ParseBasicError(ServerInfoError):
    """Bad parse on basic info"""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class ParseDayError(ServerInfoError):
    """Bad parse on day info"""
    def __init__(self, message):
        self.message = message
