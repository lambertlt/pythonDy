"""
Version: 1.0
Autor: 兰田 Lambert_work@163.com
Date: 2025-02-25 16:32:40
LastEditors: lambertlt lambert_Y_Y@163.com
LastEditTime: 2025-03-08 10:52:39
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# new
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium.webdriver.common.action_chains import ActionChains
from requests.exceptions import Timeout, RequestException
from pydub import AudioSegment
from pydub.playback import play
from threading import Thread, Lock
import time
import re
import pickle
import pyautogui
import random
import requests
import json

with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


def juliangbaiying_login():
    global data
    chrome_options = Options()
    set_options(chrome_options)
    # service = Service(ChromeDriverManager().install())
    service = Service(executable_path=data["executable_path"])
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1483, 1080)
    driver.get("https://www.baidu.com/")
    script = """var his = ['百度。https://www.baidu.com/','百度搜索hello。https://www.baidu.com/s?wd=hello','百度搜索抖音。https://www.baidu.com/s?wd=抖音'];
his.forEach(item =>{let [title, url]=item.split('。');document.title=title;history.pushState({}, '', url);});"""
    driver.execute_script(script)
    time.sleep(0.5)

    driver.get(data["url-juliangbaiying-login"])

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "index_module__title___b535e"))
    )
    driver.execute_script("window.open();")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(data["url-juliangbaiying-control"])
    for item in range(len(data["goods"])):
        id = data["goods"][item]["promotion_id"]
        url = f"https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?id={id}"
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)
        elements = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        time.sleep(1)
        if elements:
            src = elements.get_attribute("src")
            data["goods"][item]["video_url"] = src
        time.sleep(2)
    # driver.refresh()
    return driver


def set_options(chrome_options):
    global data
    ua = UserAgent()
    s = data["ua_user"]
    user_data_dir = data["user_data_dir"]
    profile_directory = data["profile_directory"]  # 替换为你的配置文件目录
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"--profile-directory={profile_directory}")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument(f"user-agent={s}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--remote-debugging-port=9222")

juliangbaiying_login()
