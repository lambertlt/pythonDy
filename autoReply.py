"""
Version: 1.0
Autor: Lambert_work@163.com
Date: 2025-02-25 10:21:12
LastEditors: lambertlt lambert_Y_Y@163.com
LastEditTime: 2025-02-25 10:21:25
"""

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

with open('data.json', 'r', encoding='utf-8') as file:
    # 使用json.load()方法将文件内容解析为Python对象(通常是dict或者list)
    data = json.load(file)

# live_url = "https://live.douyin.com/540517338200"
# flag params
last_time_name = ""
comment_list = []
list_person = []
last_comment = ""
is_typing = False
is_audio_playing = False
lock = Lock()

# 主函数


def main_douyin():
    driver = douyin_login()
    input("登陆成功后，点击回车键继续")
    update_cookies(driver)
    operating(driver)
    driver.quit()


# 操作
def operating(driver):
    global data
    time.sleep(2)
    driver.get(data['live_url'])
    # pyautogui.press("p")
    input("点击回车键开始助播程序")
    send_comment(driver, "直播助手进入直播间...")
    data['like_play_audio_start_time'] = int(time.time())
    data['welcome_play_audio_start_time'] = int(time.time())
    data['welcome_start_time'] = int(time.time())
    data['auto_send_start_time'] = int(time.time())
    data['hello_new_person_start_time'] = int(time.time())

    while True:
        get_new_notice(driver)
        hello_new_person(driver)
        get_new_comment(driver)
        auto_send_comment(driver)
        time.sleep(data['t'])


# 自动发送带节奏评论
def auto_send_comment(driver):
    global data
    now_time = int(time.time())
    if now_time - data['auto_send_start_time'] > data['auto_send_frequency']:
        if is_typing == True:
            while True:
                time.sleep(0.5)
                if is_typing == False:
                    break
        if data['auto_send_list_once'] == "True":
            for i in data['auto_send_onece_list']:
                send_comment(driver, i)
        elif data['auto_send_list_once'] == "False":
            send_comment(driver, random.choice(data['auto_send_list']))
        data['auto_send_start_time'] = int(time.time())


# 获取新评论
def get_new_comment(driver):
    global last_comment, comment_list
    element_list = driver.find_elements(
        By.CLASS_NAME, "webcast-chatroom___content-with-emoji-text"
    )
    if (
        len(element_list) > 0
        and element_list[len(element_list) - 1].text != last_comment
        and is_in_second_values(element_list[len(element_list) - 1].text)
    ):
        comment = element_list[len(element_list) - 1].text
        comment_list.append(comment)
        last_comment = comment
        print("新评论：", comment)
        handle_comment(driver)


# 判断s是否在字典的value中，存在返回false
def is_in_second_values(s):
    global data
    for item in data['auto_reply_list']:
        for i in range(1, len(item)):
            if item[i] == s:
                return False
    for n in data['auto_send_list']:
        if n == s:
            return False
    return True


# 处理评论
def handle_comment(driver):
    global comment_list, is_typing, data
    if len(comment_list) > 0:
        for item in comment_list:
            index = 0
            for p in data['auto_reply_list']:
                pattern = re.compile(re.escape(p[0]))
                matched_strings = pattern.findall(item)
                if len(matched_strings) > 0:
                    print("匹配结果：", matched_strings)
                    if is_typing == True:
                        time.sleep(1)
                    n = len(data['auto_reply_list'][index])
                    for i in range(1, n):
                        if is_typing == True:
                            while True:
                                time.sleep(0.5)
                                if is_typing == False:
                                    break
                        send_comment(driver, data['auto_reply_list'][index][i])
                    try:
                        comment_list.remove(item)
                    except:
                        pass
                index += 1
        comment_list.clear()

# 定义线程要运行的函数


def thread_function_playing_audio(path):
    global is_audio_playing
    if is_audio_playing == False:
        print(f"多线程播放 {path} 路径音频")
        with lock:
            is_audio_playing = True
        audio = AudioSegment.from_wav(path)
        play(audio)
        with lock:
            is_audio_playing = False
        print(f"多线程播放 {path} 路径音频 结束")
    else:
        print(f'由于音频被占用该 {path} 路径音频未播放')

# 获取新信息


def get_new_notice(driver):
    global data, last_time_name, is_audio_playing
    element = driver.find_element(
        By.CLASS_NAME, "webcast-chatroom___bottom-message")
    element_text = element.text
    if last_time_name == element_text:
        return
    elif len(element_text.split("：")) > 1 and element_text.split("：")[1] == "为主播点赞了":
        # 感谢点赞音频
        now_time = int(time.time())
        if now_time - data['like_play_audio_start_time'] > data['like_play_audio_frequency']:
            audio = random.choice(data['like_audio_list'])
            x = Thread(target=thread_function_playing_audio, args=(audio,))
            thread_function_playing_audio(audio)
            x.start()
        return
    elif len(element_text.split(" ")) > 1 and element_text.split(" ")[1] == "来了":
        print(element_text)
        name = filter_special_chars(element_text.split(" ")[0])
        if len(list_person) > 5:
            temp = list_person[len(list_person) - 1]
            list_person.clear()
            list_person.append(temp)
        list_person.append(name)
        last_time_name = element_text


# 欢迎新人
def hello_new_person(driver):
    global data
    now_time = int(time.time())
    if now_time - data['hello_new_person_start_time'] >= data['hello_new_person_frequency']:
        if len(list_person) > 0:
            random.shuffle(data['chars'])
            # 欢迎音频
            now_time = int(time.time())
            if now_time - data['welcome_play_audio_start_time'] > data['welcome_play_audio_frequency']:
                audio = random.choice(data['welcome_audio_list'])
                x = Thread(target=thread_function_playing_audio, args=(audio,))
                x.start()
                data['welcome_play_audio_start_time'] = int(time.time())
            if now_time - data['welcome_start_time'] > data['welcome_frequency']:             
                text = (
                    "欢迎："
                    + '"'
                    + list_person[0]
                    + ' " 进入直播间!'
                    + random.choice(data['chars'])
                )
                if is_typing == True:
                    while True:
                        time.sleep(0.5)
                        if is_typing == False:
                            break
                send_comment(driver, text)
                print(text)
                list_person.pop(0)
                data['hello_new_person_start_time'] = int(time.time())


#  发送评论内容
def send_comment(driver, comment):
    global is_typing, data
    is_typing = True
    element = driver.find_element(By.CLASS_NAME, data['comment_box_class'])
    click_element(driver, element)
    type_character(element, comment)
    pyautogui.press("enter")
    is_typing = False


# 点击元素
def click_element(driver, element):
    action = ActionChains(driver)
    action.move_to_element(element).click().perform()
    time.sleep(1)


# 打字输入
def type_character(element, text):
    global data
    if data['type_character_feign'] == "True":
        for char in text:
            wait_time = random.uniform(0.09, 0.3)
            element.send_keys(char)
            time.sleep(wait_time)
    elif data['type_character_feign'] == "False":
        element.send_keys(text)

        # 过滤掉字符串中的特殊字符和表情符号，只保留汉字、英文字母、数字和常见标点符号


def filter_special_chars(text):
    # 正则表达式模式，匹配汉字、英文字母、数字和常见标点符号
    pattern = r"[^\w\u4e00-\u9fff\s\.\,\!\?\;\:\-$$]"
    # \w 匹配字母数字下划线，\u4e00-\u9fff 匹配汉字，其他为常见标点符号
    if text == "":
        return ""
    # 使用 sub 函数替换掉所有不匹配该模式的字符为空格
    result = re.sub(pattern, "", text)
    # 移除多余的空格，使输出更加整洁
    result = re.sub(r"\s+", " ", result).strip()
    if result == "":
        return "表情用户"
    return result


# 打开抖音进行登陆
def douyin_login():
    global data
    chrome_options = Options()
    set_options(chrome_options)
    # service = Service(ChromeDriverManager().install())
    service = Service(executable_path=data['executable_path'])
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1483, 1080)
    driver.get("https://www.baidu.com/")
    script = """var his = ['百度。https://www.baidu.com/','百度搜索hello。https://www.baidu.com/s?ie=UTF-&wd=hello','百度搜索抖音。https://www.baidu.com/s?ie=UTF-8&wd=抖音'];
his.forEach(item =>{let [title, url]=item.split('。');document.title=title;history.pushState({}, '', url);});"""
    driver.execute_script(script)
    time.sleep(1)
    driver.get("https://www.douyin.com/")
    script = """var his = ['抖音。https://www.douyin.com/?recommend=1','抖音记录美好生活。https://www.douyin.com/follow','我的抖音。https://www.douyin.com/user/self?from_tab_name=main&showTab=like'];
his.forEach(item =>{let [title, url]=item.split('。');document.title=title;history.pushState({}, '', url);});"""
    driver.execute_script(script)
    load_cookies(driver)
    pyautogui.press("down")
    return driver


# 保存 Cookie
def save_cookies(driver, filename=data['cookiePklPath']):
    input("请手动登录后按回车键继续...")
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print(f"Cookie 已保存到 {filename}")


def update_cookies(driver, filename=data['cookiePklPath']):
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print(f"Cookie 已更新 {filename}")


# 加载Cookie
def load_cookies(driver, filename=data['cookiePklPath']):
    cookies = pickle.load(open(filename, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(2)


# 配置浏览器
def set_options(chrome_options):
    global data
    ua = UserAgent()
    s = data['ua_user']
    # 指定 Chrome 用户配置文件路径
    user_data_dir = data['user_data_dir']
    profile_directory = data['profile_directory']  # 替换为你的配置文件目录
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    # chrome_options.add_argument(f"--profile-directory={profile_directory}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"user-agent={s}")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
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
