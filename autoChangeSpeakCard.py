from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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

t = 0.5

with open("goods.json", "r", encoding="utf-8") as file:
    # 使用json.load()方法将文件内容解析为Python对象(通常是dict或者list)
    data = json.load(file)


# 主函数


def main_douyin():
    driver = juliangbaiying_login()
    input("登陆成功后，点击回车键继续")
    # update_cookies(driver)
    operating(driver)
    driver.quit()


# 操作
def operating(driver):
    global data, t

    while True:

        time.sleep(10)


def juliangbaiying_login():
    global data
    chrome_options = Options()
    set_options(chrome_options)
    # service = Service(ChromeDriverManager().install())
    service = Service(executable_path="./chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1483, 1080)
    driver.get(data["url-juliangbaiying-logo"])
    # script = """"""
    # driver.execute_script(script)
    # save_cookies(driver, data["cookiePklPath"])
    # load_cookies(driver, data["cookiePklPath"])
    # pyautogui.press("down")
    return driver


# 保存 Cookie
def save_cookies(driver, filename):
    input("请手动登录后按回车键继续...")
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print(f"Cookie 已保存到 {filename}")


def update_cookies(driver, filename):
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print(f"Cookie 已更新 {filename}")


# 加载Cookie
def load_cookies(driver, filename):
    cookies = pickle.load(open(filename, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    time.sleep(2)
    driver.refresh()


# 配置浏览器
def set_options(chrome_options):
    global data
    ua = UserAgent()
    s = data["ua_user"]
    # 指定 Chrome 用户配置文件路径
    # user_data_dir = data["user_data_dir"]
    # profile_directory = data["profile_directory"]  # 替换为你的配置文件目录
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    # chrome_options.add_argument(f"--profile-directory={profile_directory}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"user-agent={s}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-extensions")
    # 设置浏览器指纹
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--remote-debugging-port=9222")


# 获取数据
def fetch_data(url):
    try:
        # 发送 GET 请求，并设置超时时间为 5 秒
        response = requests.get(url, timeout=5)

        # 检查响应状态码
        if response.status_code == 200:
            # 将响应内容解析为 JSON 格式
            data = response.json()
            return data
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except Timeout:
        print("请求超时")
        return None
    except RequestException as e:
        print(f"请求发生错误: {e}")
        return None


# 运行主函数
main_douyin()
