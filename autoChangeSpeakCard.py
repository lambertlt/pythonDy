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
from pathlib import Path
import cv2
import numpy as np
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
# a.map(e=>{return{
#     'title':e.title,
#     'promotion_id':e.promotion_id,
#     'elastic_title':e.elastic_title
# }})
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
    # delete_directory(data[''])
    driver_handler = juliangbaiying_login()
    driver_speaker = noiz_login()
    time.sleep(3)
    operating(driver_handler, driver_speaker)
    driver_handler.quit()
    driver_speaker.quit()


def delete_directory(path):
    shutil.rmtree(path)


# 操作
def operating(driver_handler, driver_speaker):
    global data, t, good_video_duration, is_good_video_play
    good_index = 0
    promotion_slogans_index = 0
    sentence = ''
    sale = ''
    data['auto_send_start_time'] = int(time.time())
    driver_speaker.execute_script(f"let nowGoodId = 0")

    while True:
        auto_send_comment(driver_handler)
        now_good_id = data['goods'][good_index]['promotion_id']
        random_float = random.uniform(0, 1)
        if random_float > 0.5:
            sentence = data['promotion_slogans'][promotion_slogans_index]
        if random_float > 0.7:
            sale = random.choice(["是一个爆款", "是一个热销款"])
        if random_float > 0.8:
            random.shuffle(data['live_interval_audio_list'])
            request = f"""
                nowGoodId ={ now_good_id }
                window.audioPlaybackCompleted = false;
                const formData = new FormData();
                formData.append('text', '{random.choice(data['live_interval_audio_list'])}');
                formData.append('voice_id', '{random.choice(data['voice_id'])}');
                formData.append('quality_preset', '0');
                formData.append('output_format', 'wav');
                formData.append('target_lang', '');
                formData.append('speed', '1');

                fetch('https://noiz.ai/api/v1/text-to-speech-long?language=zh', {{
                    method: 'POST',
                    body: formData,
                }})
                .then(response => {{
                    let goodId = {now_good_id}
                    if (!response.ok) {{
                        throw new Error('Network response was not ok');
                    }}
                    if (response.headers.get('content-type') === 'audio/wav' && goodId==nowGoodId) {{
                        return response.blob();
                    }}
                    return response.json(); // 或者response.text()，根据实际情况
                }})
                .then(blob => {{
                    let goodId = {now_good_id}
                    if(goodId==nowGoodId){{
                        const audioUrl = URL.createObjectURL(blob);
                        const audio = new Audio(audioUrl);

                        audio.addEventListener('ended', () => {{
                            URL.revokeObjectURL(audioUrl);
                            window.audioPlaybackCompleted = true;
                        }});
                        audio.play()
                    }}
                    
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
            nowGoodId ={ now_good_id }
            window.audioPlaybackCompleted = false;
            const formData = new FormData();
            formData.append('text','{random.choice(["接下来这款","下一款"])}{sale}发卡：{data['goods'][good_index]['elastic_title']},现在活动价,仅需{data['goods'][good_index]['price_desc']['min_price']['integer']}.{data['goods'][good_index]['price_desc']['min_price']['decimal']}元，在小黄车{good_index+1}号链接 {random.choice(["赶快冲它","大家可以点开看看","真的很合适",""])}！{sentence}') 
            formData.append('voice_id','{random.choice(data['voice_id'])}')
            formData.append('quality_preset','0')
            formData.append('output_format','wav')
            formData.append('target_lang','')
            formData.append('speed','1')
            fetch('https://noiz.ai/api/v1/text-to-speech-long?language=zh', {{
                method: 'POST',
                body: formData, // 直接将FormData对象作为请求体
            }})
            .then(response => {{
                let goodId = {now_good_id}
                if (!response.ok) {{
                    throw new Error('Network response was not ok');
                }}
                if (response.headers.get('content-type') === 'audio/wav' && goodId==nowGoodId) {{
                    return response.blob(); // 将响应体转换为 Blob
                }}
                return response.json(); // 或者response.text()，根据实际情况
            }})
            .then(blob => {{
                    let goodId = {now_good_id}
                    if(goodId==nowGoodId){{
                        const audioUrl = URL.createObjectURL(blob); // 创建一个对象URL
                        const audio = new Audio(audioUrl); // 创建一个Audio对象
                        audio.addEventListener('ended', () => {{
                            URL.revokeObjectURL(audioUrl);
                            window.audioPlaybackCompleted = true;
                        }});
                        audio.play(); // 播放音频
                    }}
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
            try:
                good_video_duration = 0
                video_path = f"{data['videos_path']}/{now_good_id}/{now_good_id}.mp4"
                if os.path.exists(video_path):
                    x = Thread(target=play_good_video, args=(video_path,))
                    x.start()
                else:
                    img_path = f"{data['videos_path']}/{now_good_id}/"
                    x = Thread(target=play_good_img, args=(img_path,))
                    x.start()
                print("播放视频——脚本运行结束")
            except Exception as e:
                print(f"播放视频——发生了一个非预期的异常: {e}")
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
            print("切换讲解卡——脚本运行结束")
        except Exception as e:
            print(f"切换讲解卡——发生了一个非预期的异常: {e}")

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


# 播放图片
def play_good_img(img_url):
    image_folder = img_url
    images = [img for img in os.listdir(image_folder) if img.endswith(
        ".png") or img.endswith(".jpg") or img.endswith(".jpeg")]
    if not images:
        print("没有找到图片")
    else:
        cv2.namedWindow("Image Slideshow", cv2.WINDOW_AUTOSIZE)
        target_width = 400
        aspect_ratio = 16 / 9.0
        target_height = int(target_width * (16 / 9))
        index = 0
        while True:
            img_path = os.path.join(image_folder, images[index])
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                print(f"无法加载图像 {img_path}")
                index += 1
                if index >= len(images):
                    break
                continue
            original_height, original_width = img.shape[:2]
            ratio = target_width / float(original_width)
            new_height = int(original_height * ratio)
            if new_height > target_height:
                ratio = target_height / float(original_height)
                new_height = target_height
                target_width_temp = int(original_width * ratio)
            else:
                target_width_temp = target_width
            img_resized = cv2.resize(
                img, (target_width_temp, new_height), interpolation=cv2.INTER_AREA)
            background_color = [0, 255, 0]
            final_img = np.full((target_height, target_width, 3),
                                background_color, dtype=np.uint8)
            y_offset = int((target_height - new_height) / 2)
            x_offset = int((target_width - target_width_temp) / 2)
            if img_resized.shape[2] == 4:
                alpha_channel = img_resized[:, :, 3] / 255.0
                for c in range(0, 3):
                    final_img[y_offset:y_offset + new_height, x_offset:x_offset + target_width_temp, c] = \
                        alpha_channel * img_resized[:, :, c] + (
                            1 - alpha_channel) * final_img[y_offset:y_offset + new_height, x_offset:x_offset + target_width_temp, c]
            else:
                final_img[y_offset:y_offset + new_height,
                          x_offset:x_offset + target_width_temp, :] = img_resized
            cv2.imshow("Image Slideshow", final_img)
            if cv2.waitKey(2500) & 0xFF == ord('q'):
                break
            index += 1
            if index >= len(images):
                break
        cv2.destroyAllWindows()

# 异步播放视频


def play_good_video(video_url):
    global is_good_video_play, good_video_duration
    is_play_audio = False
    cap = cv2.VideoCapture(video_url)
    # 设置目标宽度和长宽比
    target_width = 400
    aspect_ratio = 9 / 16
    audio = AudioSegment.from_file(video_url, format="mp4")
    now_audio = audio - 35
    raw_data = now_audio.raw_data
    audio_play_obj = None

    # play_obj.wait_done()
    with lock:
        is_good_video_play = True

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval_ms = int(1000 / fps)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    with lock:
        good_video_duration = frame_count / fps
        print(f"video 播放时长：{good_video_duration}")

    start_time = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or is_good_video_play == False:
            break

        # 调整帧大小并添加绿色填充以符合目标尺寸
        processed_frame = resize_and_pad(frame, target_width, aspect_ratio)
        cv2.imshow("Video", processed_frame)
        if is_play_audio == False:
            audio_play_obj = sa.play_buffer(
                raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate
            )
            is_play_audio = True
        elapsed_time = (time.time() - start_time) * 1000
        sleep_time = max(frame_interval_ms - (elapsed_time %
                         frame_interval_ms), 1)
        time.sleep(sleep_time / 1000.0)
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


def resize_and_pad(frame, target_width, aspect_ratio):
    """根据目标宽度和长宽比调整图像大小，并在周围填充绿色"""
    original_height, original_width = frame.shape[:2]

    # 计算目标高度以匹配给定的宽高比
    target_height = int(target_width / aspect_ratio)

    # 计算缩放比例
    scale_ratio = target_width / original_width

    new_height = int(original_height * scale_ratio)

    # 调整大小
    resized_frame = cv2.resize(
        frame, (target_width, new_height), interpolation=cv2.INTER_LANCZOS4)

    # 创建一个绿色背景的画布
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    canvas[:] = (0, 255, 0)  # 绿色填充

    # 如果新高度小于目标高度，则垂直居中；否则水平居中
    if new_height < target_height:
        y_offset = (target_height - new_height) // 2
        x_offset = 0
    else:
        y_offset = 0
        x_offset = (target_width - resized_frame.shape[1]) // 2

    # 将调整后的帧放到绿色背景上
    canvas[y_offset:y_offset + new_height, x_offset:x_offset +
           resized_frame.shape[1]] = resized_frame[:, :target_width]

    return canvas

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
        type_character(name, "lambert_work@163.com")
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
    WebDriverWait(driver, 300).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "index_module__title___b535e"))
    )
    driver.execute_script("window.open();")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(data["url-juliangbaiying-control"])
    download_goods_media(driver)
    print("巨量应用 加载成功")
    return driver


def download_goods_media(driver):
    global data
    for item in range(len(data["goods"])):
        id = data["goods"][item]["promotion_id"]
        dir_path = Path(f"{data['videos_path']}/{id}")
        if dir_path.exists() and dir_path.is_dir():
            continue
        url = f"https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?id={id}"
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(0.2)
        driver.execute_script("window.open();")
        time.sleep(0.2)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(0.2)
        driver.get(url)
        time.sleep(1)
        try:
            # 下载视频
            elements = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            time.sleep(1)
            if elements:
                video_src = elements.get_attribute("src")
                download_file(
                    video_src, data['videos_path']+f"/{id}/{id}.mp4")
        except Exception:
            # 下载图片
            elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "index_module__item___ac928"))
            )
            for item1 in range(len(elements)):
                img_src = elements[item1].get_attribute("src")
                download_file(
                    img_src, data['videos_path']+f"/{id}/{item1}.jpg")
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
    print("商品资料下载完成")

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
