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
    driver_speaker = noiz_login()
    driver_handler = juliangbaiying_login()
    time.sleep(3)
    # driver.refresh()
    input("页面加载成功，enter")
    operating(driver_handler, driver_speaker)
    driver_handler.quit()
    driver_speaker.quit()


# 操作
def operating(driver_handler, driver_speaker):
    global data, t
    good_index = 0
    while True:
        time.sleep(13)
        if good_index >= len(data["goods"]):
            good_index = 0
        else:
            request = f"""
                return new Promise((resolve, reject) => {{
                    const formData = new FormData();
                    formData.append('text','{data['goods'][good_index]['title']},现在仅需{data['goods'][good_index]['price_desc']['min_price']['integer']}.{data['goods'][good_index]['price_desc']['min_price']['decimal']}') 
                    formData.append('voice_id','1c2c0a287')
                    formData.append('quality_preset','0')
                    formData.append('output_format','wav')
                    formData.append('target_lang','')
                    formData.append('speed','1')
                    fetch('https://noiz.ai/api/v1/text-to-speech-long?language=zh', {{
                        method: 'POST',
                        body: formData, // 直接将FormData对象作为请求体
                    }})
                    .then(response => {{
                        if (!response.ok) {{
                            throw new Error('Network response was not ok');
                        }}
                        if (response.headers.get('content-type') === 'audio/wav') {{
                                return response.blob(); // 将响应体转换为 Blob
                        }}
                        return response.json(); // 或者response.text()，根据实际情况
                    }})
                    .then(blob => {{
                            const audioUrl = URL.createObjectURL(blob); // 创建一个对象URL
                            const audio = new Audio(audioUrl); // 创建一个Audio对象
                            
                            // 播放结束时清除对象URL
                            audio.addEventListener('ended', () => {{
                                URL.revokeObjectURL(audioUrl);
                                resolve('异步操作已完成');
                            }});

                            audio.play(); // 播放音频
                        }})
                    .catch(error => console.error('There was a problem with the fetch operation:', error));
                }});
            """
            try:
                driver_speaker.execute_script(request)
                time.sleep(0.5)
                print("播放语音脚本运行结束")
            except Exception as e:
                print(f"发生了一个非预期的异常: {e}")
            request = f"""
            fetch('https://buyin.jinritemai.com/api/anchor/livepc/setcurrent?verifyFp=verify_m7q9579r_8gWGFJ0Q_bGZY_40ce_89y9_j24sL6TY5vxY&fp=verify_m7q9579r_8gWGFJ0Q_bGZY_40ce_89y9_j24sL6TY5vxY&msToken=pGykbqYbixZLHF3UKkIuON9LS7ao4-C0Xl2DeUgIfuotRHwgYoVduC1cjQkUS5ZB0td9QhxVzeCFpHqytyCylLdEO6xgxj2DHNkk55r9sYaAmjsNI_TfkP5qDFXDoVTq2-8ovGpumg3Zd_9GW7Nv16cTuLB9xuswCXzN7RXv2ge0tsNkJzCnRQ%3D%3D&a_bogus=mjURg7yJOqm5P3CSuCBFyfVlIUx%2FNTWy7lToSyNTCqPGGHebudpqgb2CnKLLsskj%2FRM3iIIH8EYeYfxcK2pChFrkLmhDuK06Y0IAV8sLhqq6GFG8DrRTCw0N9JGY0c4EOQKRJ1XXltQO2D5ULr-kUdAyeATJsQkpPHafDdWGxoFf6047PNFduPtdYXzx-QoRJD%3D%3D', {{
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
            random.uniform(1.5,3.5 )
            try:
                driver_handler.execute_script(request)
                print("切换讲解卡脚本运行结束")
            except Exception as e:
                print(f"发生了一个非预期的异常: {e}")
        good_index += 1


def type_character(element, text):
    element.send_keys(text)


def noiz_login():
    global data
    chrome_options = Options()
    set_options(chrome_options)
    # service = Service(ChromeDriverManager().install())
    service = Service(executable_path=data["executable_path"])
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1483, 1080)
    driver.set_script_timeout(30)
    driver.get(data["ai_audio_url_login"])
    time.sleep(3)
    try:
        name = driver.find_element(
            By.XPATH,
            "/html/body/div/section/div[2]/div/form/div[1]/div/div/div/div/div/input",
        )
        password = driver.find_element(
            By.XPATH,
            "/html/body/div/section/div[2]/div/form/div[2]/div/div/div/div/div/span/input",
        )
        login = driver.find_element(
            By.XPATH,
            "/html/body/div/section/div[2]/div/form/div[4]/div/div/div/div/button",
        )
        type_character(name, "lambert_Y_Y@163.com")
        type_character(password, "lanTIAN123")
        time.sleep(1)
        login.click()
        print("登陆成功")
        time.sleep(2)
    except Exception as e:
        print(f"登陆失败，发生了一个非预期的异常: {e}")
    return driver


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
