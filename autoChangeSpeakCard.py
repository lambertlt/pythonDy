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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cv2
import simpleaudio as sa
import os
import time
import re
import pickle
import pyautogui
import random
import requests
import json
import shutil
lock = Lock()
# flag
t = 0.5
audo_send_index = 0
is_good_video_play = False
good_video_duration = 0

with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# 主函数


def main_douyin():
    global data
    driver_handler = juliangbaiying_login()
    driver_speaker = noiz_login()
    time.sleep(3)
    operating(driver_handler, driver_speaker)
    driver_handler.quit()
    driver_speaker.quit()


# 操作
def operating(driver_handler, driver_speaker):
    global data, t, good_video_duration, is_good_video_play
    good_index = 0
    promotion_slogans_index = 0
    data['auto_send_start_time'] = int(time.time())

    while True:
        auto_send_comment(driver_handler)
        random_float = random.uniform(0, 1)
        sentence = ''
        sale = ''
        if random_float > 0.5:
            sentence = data['promotion_slogans'][promotion_slogans_index]
        if random_float > 0.7:
            sale = random.choice(["是一个爆款", "是一个热销款"])
        if random_float > 0.3:
            random.shuffle(data['live_interval_audio_list'])
            request = f"""
                window.audioPlaybackCompleted = false;
                const formData = new FormData();
                formData.append('text', '{random.choice(data['live_interval_audio_list'])}');
                formData.append('voice_id', '1c2c0a287');
                formData.append('quality_preset', '0');
                formData.append('output_format', 'wav');
                formData.append('target_lang', '');
                formData.append('speed', '1');

                fetch('https://noiz.ai/api/v1/text-to-speech-long?language=zh', {{
                    method: 'POST',
                    body: formData,
                }})
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error('Network response was not ok');
                    }}
                    if (response.headers.get('content-type') === 'audio/wav') {{
                        return response.blob();
                    }}
                    return response.json(); // 或者response.text()，根据实际情况
                }})
                .then(blob => {{
                    const audioUrl = URL.createObjectURL(blob);
                    const audio = new Audio(audioUrl);

                    audio.addEventListener('ended', () => {{
                        URL.revokeObjectURL(audioUrl);
                        window.audioPlaybackCompleted = true;
                    }});
                    audio.play()
                }})
                .catch(error => {{
                    console.error('There was a problem with the fetch operation:', error);
                    reject(error);
                }});
            """
            try:
                driver_speaker.execute_script(request)
                wait_for_audio_completion(
                    driver_speaker,  "window.audioPlaybackCompleted;")
                print("播放场控语音——脚本运行结束")
            except Exception as e:
                print(f"播放场控语音——发生了一个非预期的异常: {e}")

        request = f"""
            window.speakCardCompleted = false;
            fetch('https://buyin.jinritemai.com/api/anchor/livepc/setcurrent?verifyFp=verify_m7q9579r_8gWGFJ0Q_bGZY_40ce_89y9_j24sL6TY5vxY&fp=verify_m7q9579r_8gWGFJ0Q_bGZY_40ce_89y9_j24sL6TY5vxY&msToken=hkcfl9bKA_bykhNFw2tR1yCANvPuw1XHQ4erPqJeN8-abNLXL_vvdJULE2bX1HrtTVKVEMxuX71Z0U_qXv2ylB1iELWJRBeY6f6yi6hDQGVWCY-ce8tJ6qYLsWecxl-rUXme2ZSJRl9Jhpkn9NNZK15mux517fZxAtWTR8zbym9C&a_bogus=m6s5h7XwQp8VepASmCppyArlA8DlrsWyEMTxSy1PSoKtG1FYn2pPDGhgJOLy49JRBWBrie-7MEuKbxdb%2FVp9hq9kFmhvSuiWT4IAV0mL8qqXGz48ErfwCwmNtJGbUcTEO5KbJI61AtmO2DOUEr3hUp5y9ATJsQipPrrbDBRGPoFv6F47MNqxuNtDiXFx-5I4kj%3D%3D', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded',
                }},
                body: 'promotion_id={data['goods'][good_index]['promotion_id']}&cancel=false',
                credentials: 'include', 
                }})
                .then(response => {{response.json();window.speakCardCompleted = true;}})
                .then(data => console.log(data))
                .catch((error) => {{
                    console.error('Error:', error);
                }});
        """
        try:
            driver_handler.execute_script(request)
            wait_for_audio_completion(
                driver_handler, "window.speakCardCompleted;")
            print("第一次切换讲解卡——脚本运行结束")
        except Exception as e:
            print(f"第一次切换讲解卡——发生了一个非预期的异常: {e}")
        request = f"""
            window.audioPlaybackCompleted = false;
            const formData = new FormData();
            formData.append('text','{random.choice(["接下来这款","下一款"])}{sale}发卡：{data['goods'][good_index]['title']},现在活动价,仅需{data['goods'][good_index]['price_desc']['min_price']['integer']}.{data['goods'][good_index]['price_desc']['min_price']['decimal']}元，在小黄车{good_index+1}号链接 {random.choice(["赶快冲它","大家可以点开看看","真的很合适",""])}！{sentence}') 
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
                    audio.addEventListener('ended', () => {{
                        URL.revokeObjectURL(audioUrl);
                        window.audioPlaybackCompleted = false;
                    }});
                    audio.play(); // 播放音频
                }})
            .catch(error => console.error('There was a problem with the fetch operation:', error));
        """
        try:
            audio = AudioSegment.from_file("./audio/ding.mp3")
            audio = audio - 35
            play(audio)
            driver_speaker.execute_script(request)
            wait_for_audio_completion(
                driver_speaker, "window.audioPlaybackCompleted;")
            print("播放讲解卡标题——脚本运行结束")
        except Exception as e:
            print(f"播放讲解卡标题——发生了一个非预期的异常: {e}")
        # 切讲解卡
        request = f"""
            window.speakCardCompleted = false;
            fetch('https://buyin.jinritemai.com/api/anchor/livepc/setcurrent?verifyFp=verify_m7q9579r_8gWGFJ0Q_bGZY_40ce_89y9_j24sL6TY5vxY&fp=verify_m7q9579r_8gWGFJ0Q_bGZY_40ce_89y9_j24sL6TY5vxY&msToken=hkcfl9bKA_bykhNFw2tR1yCANvPuw1XHQ4erPqJeN8-abNLXL_vvdJULE2bX1HrtTVKVEMxuX71Z0U_qXv2ylB1iELWJRBeY6f6yi6hDQGVWCY-ce8tJ6qYLsWecxl-rUXme2ZSJRl9Jhpkn9NNZK15mux517fZxAtWTR8zbym9C&a_bogus=m6s5h7XwQp8VepASmCppyArlA8DlrsWyEMTxSy1PSoKtG1FYn2pPDGhgJOLy49JRBWBrie-7MEuKbxdb%2FVp9hq9kFmhvSuiWT4IAV0mL8qqXGz48ErfwCwmNtJGbUcTEO5KbJI61AtmO2DOUEr3hUp5y9ATJsQipPrrbDBRGPoFv6F47MNqxuNtDiXFx-5I4kj%3D%3D', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded',
                }},
                body: 'promotion_id={data['goods'][good_index]['promotion_id']}&cancel=false',
                credentials: 'include', 
                }})
                .then(response => {{response.json();window.speakCardCompleted = true;}})
                .then(data => console.log(data))
                .catch((error) => {{
                    console.error('Error:', error);
                }});
        """
        try:
            driver_handler.execute_script(request)
            wait_for_audio_completion(
                driver_handler, "window.speakCardCompleted;")
            print("第二次切换讲解卡——脚本运行结束")
        except Exception as e:
            print(f"第二次切换讲解卡——发生了一个非预期的异常: {e}")
        try:
            good_video_duration = 0
            video_path = f"{data['videos_path']}/{good_index}.mp4"
            if os.path.exists(video_path):
                x = Thread(target=play_good_video, args=(video_path,))
                x.start()
            print("播放视频——脚本运行结束")
        except Exception as e:
            print(f"播放视频——发生了一个非预期的异常: {e}")

        good_index += 1
        promotion_slogans_index += 1
        if good_index >= len(data["goods"]):
            good_index = 0
        if promotion_slogans_index >= len(data['promotion_slogans']):
            promotion_slogans_index = 0
        time.sleep(good_video_duration)
        is_good_video_play == False


def wait_for_audio_completion(driver, params, timeout=30):
    while (True):
        completed = driver.execute_script(
            f"return {params}")
        if completed or timeout == 0:
            print("音频播放完成")
            break
        # print("音频仍在播放...")
        time.sleep(1)
        timeout -= 1
    driver.execute_script(
        "window.audioPlaybackCompleted=false;window.speakCardCompleted = false;")

# 异步播放视频


def play_good_video(video_url):
    global is_good_video_play, good_video_duration
    is_play_audio = False
    cap = cv2.VideoCapture(video_url)
    audio = AudioSegment.from_file(video_url, format="mp4")
    now_audio = audio - 35
    raw_data = now_audio.raw_data
    audio_play_obj = None

    # play_obj.wait_done()
    with lock:
        is_good_video_play = True

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval_ms = int(1000 / fps)  # 计算每帧之间的间隔时间(ms)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    with lock:
        good_video_duration = frame_count / fps
        print(f"video 播放时长：{good_video_duration}")

    start_time = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or is_good_video_play == False:
            break
        current_time = time.time() - start_time
        frame_number = int(current_time * fps)
        cv2.imshow("Video", frame)
        if is_play_audio == False:
            audio_play_obj = sa.play_buffer(
                raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate
            )
            is_play_audio = True
        # 控制帧率
        elapsed_time = (time.time() - start_time) * 1000
        sleep_time = max(frame_interval_ms - (elapsed_time %
                         frame_interval_ms), 1)
        time.sleep(sleep_time / 1000.0)
        # 按'q'键退出
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    # 释放资源
    if audio_play_obj != None:
        audio_play_obj.stop()
    cap.release()
    cv2.destroyAllWindows()


def welcome_people(driver):
    pass

# 自动发送带节奏评论


def auto_send_comment(driver):
    global data, audo_send_index
    now_time = int(time.time())
    if now_time - data["auto_send_start_time"] > data["auto_send_frequency"]:
        random.shuffle(data["chars"])
        if data["auto_send_list_once"] == "True":
            for i in data["auto_send_onece_list"]:
                send_comment(driver, i + random.choice(data["chars"]))
        elif data["auto_send_list_once"] == "False":
            if audo_send_index >= len(data["auto_send_list"]):
                audo_send_index = 0
                random.shuffle(data["auto_send_list"])
            send_comment(
                driver,
                data["auto_send_list"][audo_send_index] +
                random.choice(data["chars"]),
            )
            audo_send_index += 1
        data["auto_send_start_time"] = int(time.time())


def type_character(element, text):
    element.send_keys(text)

#  发送评论内容


def send_comment(driver, comment):
    request = f"""
        return new Promise((resolve, reject) => {{
            fetch('https://buyin.jinritemai.com/api/anchor/comment/operate?verifyFp=verify_m7rjs0c5_X4GLrMJp_cWHc_4WKB_BDfp_pRhJY2Z0Jaw4&fp=verify_m7rjs0c5_X4GLrMJp_cWHc_4WKB_BDfp_pRhJY2Z0Jaw4&msToken=Or-S8IPBio64jh45o-mh0yNFrWkDafQsnZBwdbrkkrrpn9gKwPuSBT6cka4Wy8mxrQs_-z-_YYuvOdxh_Ld3lljN166xM3HmNTBSbuNutFTVw0vBiQamT4AlxK8Hq27RngEcRJMC_ijzSkVvpfVWNj4i4_-OeeJpt2dviwGNKzf6DnMPTH7umqE%3D&a_bogus=EXUVkwSJOdWRFplt8KDPy6qlctfMNBWjGFi2WiHPSoO2T1zYldBpgSo1cKqG1P6RF8l-iH3Hi3POufdOKIsthzVkomhkSqh6zsAcV0vLMqNXaUk0grfhCukweJrTURTEO5oyJlX1AtQPIdQUDq3wUBl9SATE4mJpFqabDQRGxoFf6FG7PHF2uPGdThtbUG2X', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                   "content": "{comment}",
                   "operate_type": 2
                }}),
            }})
            .then(response => {{
                if (!response.ok) {{
                    throw new Error('Network response was not ok');
                }}
                return response.json(); // 或者response.text()，根据实际情况
            }})
            .then(data => {{ resolve('异步操作已完成');}})
            .catch(error => console.error('There was a problem with the fetch operation:', error));
        }});
    """
    try:
        driver.execute_script(request)
        print("发布评论——脚本运行结束")
    except Exception as e:
        print(f"发布评论——发生了一个非预期的异常: {e}")


def noiz_login():
    global data
    chrome_options = Options()
    set_options(chrome_options)
    service = Service(executable_path=data["executable_path"])
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(980, 680)
    driver.set_script_timeout(30)
    time.sleep(1)
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
        print("AI spearker 加载成功")
    except Exception as e:
        print(f"登陆失败，发生了一个非预期的异常: {e}")
    return driver


def juliangbaiying_login():
    global data
    chrome_options = Options()
    user_data_dir = data["user_data_dir"]
    profile_directory = data["profile_directory"]
    set_options(chrome_options, user_data_dir, profile_directory)
    service = Service(executable_path=data["executable_path"])
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1200, 780)
    driver.set_script_timeout(30)
    driver.get(data["url-juliangbaiying-login"])
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "index_module__title___b535e"))
    )
    driver.execute_script("window.open();")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(data["url-juliangbaiying-control"])
    if not os.path.exists(data['videos_path']):
        print(f"目录 {data['videos_path']} 不存在")
        for item in range(len(data["goods"])):
            id = data["goods"][item]["promotion_id"]
            url = f"https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?id={id}"
            driver.switch_to.window(driver.window_handles[1])
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url)
            try:
                elements = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
            except Exception:
                print("第 "+str(item) + " 没有商品视频")
                driver.close()
                driver.switch_to.window(driver.window_handles[1])
                continue
            time.sleep(1)
            if elements:
                video_src = elements.get_attribute("src")
                # data["goods"][item]["video_url"] = src
                download_file(video_src, data['videos_path']+str(item)+".mp4")
            driver.close()
# shutil.rmtree(data['videos_path'])
    print("巨量应用 加载成功")
    return driver


# 配置浏览器


def set_options(chrome_options, user_data_dir="", profile_directory=""):
    global data
    ua = UserAgent()
    s = data["ua_user"]
    if user_data_dir != "" and profile_directory != "":
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"--profile-directory={profile_directory}")
    chrome_options.add_argument(f"user-agent={s}")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    # chrome_options.add_argument("--remote-debugging-port=9222")


def download_file(url, save_path):
    """
    下载文件并保存到指定路径。

    :param url: 文件的URL地址
    :param save_path: 文件保存的完整路径（包括文件名）
    """
    # 确保保存目录存在，如果不存在则创建
    directory = os.path.dirname(save_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 发送HTTP GET请求
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 检查请求是否成功

    # 将下载的内容写入文件
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # 过滤掉保持活动连接的空块
                file.write(chunk)


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
