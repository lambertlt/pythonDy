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

with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# 主函数


def main_douyin():
    global data
    driver = juliangbaiying_login()
    time.sleep(3)
    # driver.refresh()
    input("页面加载成功，enter")
    operating(driver)
    driver.quit()


# 操作
def operating(driver):
    global data, t
    good_index = 0
    while True:
        time.sleep(random.uniform(10, 13))
        if good_index < len(data["goods"]):
            good_index += 1
        else:
            good_index = 0
        request = f"""
        fetch('
https://buyin.jinritemai.com/api/anchor/livepc/setcurrent?verifyFp=verify_m7oqxwxt_4inpOvzz_WcOZ_4UeK_BZ2d_eV4YznJCKriy&fp=verify_m7oqxwxt_4inpOvzz_WcOZ_4UeK_BZ2d_eV4YznJCKriy&msToken=Ai-L7KysDnATFt-AWGcqyTAHKpRWcTEoArmCWKGOXWMNRsSKT6xNge7eSRPDokTf_YmoF0XTi7C6pqJPFsroZvQ_ux6EN_qYelgyf_XrJk4xY6pSQZ9gay52GXm5LRucoQeEmX8Wn1OfaBhpngCbSVUPtEu9WUfbE4SGSqD9hA84reJM9xELd0c%3D&a_bogus=E6UjDHy7YZRjO3lS8CDheAIUAI9MNsWj-BiKSHnP9FYpG7zGjdpZEwPobqOJpbbazSB-w1QHoEldGEDbQdsdMqIkqmpfSutjFzAcIhsLgqqfTz7DLHShCwuzLwBKlchLa%2FcXEIs5IssEgEclnrATlBpaC5TLmmmpWHFjdZScj9RTDALP83aSOMwANfwKmY2RRD%3D%3D', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/x-www-form-urlencoded',
            }},
            body: 'promotion_id={data['goods'][good_index]['promotion_id']}&cancel=false',
            credentials: 'include', 
            }})
            .then(response => response.json())
            .then(data => console.log(data))
            .catch((error) => {{
                console.error('Error:', error);
        }});
        """
        print(request)
        try:
            driver.execute_script(request)
        except Exception as e:
            print(f"发生了一个非预期的异常: {e}")


def juliangbaiying_login():
    global data
    chrome_options = Options()
    set_options(chrome_options)
    # service = Service(ChromeDriverManager().install())
    service = Service(executable_path=data["executable_path"])
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1483, 1080)
    driver.get(data["url-juliangbaiying-login"])
    input("登陆成功后，点击回车键继续")
    driver.execute_script("window.open();")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(data["url-juliangbaiying-control"])
    time.sleep(2)
    # driver.refresh()
    return driver


# 配置浏览器


def set_options(chrome_options):
    global data
    ua = UserAgent()
    s = data["ua_user"]
    chrome_options = webdriver.ChromeOptions()
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
