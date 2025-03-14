from seleniumwire import webdriver as webdriver_wire
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium.webdriver.common.action_chains import ActionChains
from requests.exceptions import Timeout, RequestException
from pydub.playback import _play_with_simpleaudio
from pydub import AudioSegment
from pydub.playback import play
from threading import Thread, Lock
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from glob import glob
import cv2
import importlib
import numpy as np
import simpleaudio as sa
import brotli
import os
import time
import re
import pickle
import pyautogui
import random
import requests
import json
import shutil


with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


class PlayAudio:
    def __init__(self):
        self.audio_path = None
        self.volume = None
        print("PlayAudio")

    def mp3_play_async(self, audio_path, volume=-30):
        x = Thread(target=self.mp3_play, args=(audio_path, volume,))
        x.daemon = True
        x.start()
        return x

    def mp3_play(self, audio_path, volume=-30):
        self.volume = volume
        self.audio_path = audio_path
        audio = AudioSegment.from_file("./audio/ding.mp3")
        audio = audio + self.volume
        play(audio)


class PlayImg:
    def __init__(self):
        self.img_length = 0
        self.bg_color = None
        self.window_name = None
        self.wait_time = None
        print('PlayImg')

    def play_async(self, folder_path, wait_time=3000, bg_color=[0, 255, 0], width=400, window_name="python.exe"):
        x = Thread(target=self.play, args=(
            folder_path, wait_time, bg_color, width, window_name,))
        x.daemon = True
        x.start()
        return x

    def play(self, folder_path, wait_time=3000, bg_color=[0, 255, 0], width=400, window_name="python.exe"):
        self.bg_color = bg_color
        self.window_name = window_name
        self.wait_time = wait_time
        fixed_width = width
        target_ratio = 9 / 16

        # 获取目录下所有图片文件路径
        image_paths = glob(os.path.join(folder_path, '*'))
        image_paths = [img for img in image_paths if img.lower().endswith(
            ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'))]

        if not image_paths:
            print("No images found in the specified directory.")
            return

        wait_time = self.wait_time  # 每张图片显示的时间为1秒（单位：毫秒）

        for image_path in image_paths:
            frame = cv2.imread(image_path)
            if frame is None:
                print(f"Failed to load image {image_path}")
                continue

            h, w, _ = frame.shape
            original_ratio = w / h

            # 如果原图片的宽高比大于目标宽高比，说明原图片更“宽”
            if original_ratio > target_ratio:
                new_width = fixed_width
                new_height = int(fixed_width / original_ratio)
            else:  # 否则，原图片更“高”
                new_width = int(fixed_width * original_ratio / target_ratio)
                new_height = int(fixed_width / target_ratio)

            # 调整帧大小以匹配新的尺寸，同时保持原图片的比例
            frame_resized = cv2.resize(
                frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

            # 创建一个新的帧，用指定颜色填充作为背景
            background_frame = np.zeros(
                (int(fixed_width / target_ratio), fixed_width, 3), dtype=np.uint8)
            background_frame[:] = self.bg_color  # 设置为指定背景色

            # 将调整大小后的图片放置到背景帧中心位置
            y_offset = (background_frame.shape[0] - new_height) // 2
            x_offset = (background_frame.shape[1] - new_width) // 2

            background_frame[y_offset:y_offset + new_height,
                             x_offset:x_offset + new_width] = frame_resized

            # 显示处理后的帧
            cv2.imshow(self.window_name, background_frame)

            # 等待一段时间再显示下一帧，模拟图片轮播速度
            if cv2.waitKey(wait_time) & 0xFF == ord('q'):
                break

        # 关闭所有OpenCV窗口
        cv2.destroyAllWindows()


class PlayVideo:
    def __init__(self):
        self.video_length = 0
        self.bg_color = None
        self.window_name = None
        print('PlayVideo')

    def play_async(self, video_path, bg_color=[0, 255, 0], width=400, volume=-15, window_name="python.exe"):
        x = Thread(target=self.play, args=(
            video_path, bg_color, width, volume, window_name,))
        x.daemon = True
        x.start()
        return x

    def play(self, video_path, bg_color=[0, 255, 0], width=400, volume=-15, window_name="Video Player"):
        # 提取并播放音频
        audio = AudioSegment.from_file(video_path)
        audio = audio + volume
        audio_thread = Thread(target=_play_with_simpleaudio, args=(audio,))
        audio_thread.daemon = True
        audio_thread.start()

        self.window_name = window_name
        self.bg_color = bg_color
        fixed_width = width
        target_ratio = 9 / 16

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            h, w, _ = frame.shape
            original_ratio = w / h

            if original_ratio > target_ratio:
                new_width = fixed_width
                new_height = int(fixed_width / original_ratio)
            else:
                new_width = int(fixed_width * original_ratio / target_ratio)
                new_height = int(fixed_width / target_ratio)

            frame_resized = cv2.resize(
                frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

            background_frame = np.zeros(
                (int(fixed_width / target_ratio), fixed_width, 3), dtype=np.uint8)
            background_frame[:] = self.bg_color

            y_offset = (background_frame.shape[0] - new_height) // 2
            x_offset = (background_frame.shape[1] - new_width) // 2

            background_frame[y_offset:y_offset + new_height,
                             x_offset:x_offset + new_width] = frame_resized

            cv2.imshow(self.window_name, background_frame)

            if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        audio_thread.join()  # 等待音频播放完成

    def play_mute_async(self, video_path, bg_color=[0, 255, 0], width=400, window_name="python.exe"):
        x = Thread(target=self.play_mute, args=(
            video_path, bg_color, width, window_name,))
        x.start()
        return x

    def play_mute(self, video_path, bg_color=[0, 255, 0], width=400, window_name="python.exe"):
        self.window_name = window_name
        self.bg_color = bg_color
        # 固定宽度和目标宽高比
        fixed_width = 400
        target_ratio = 9 / 16

        # 打开视频文件
        cap = cv2.VideoCapture(video_path)

        # 获取原始视频的帧率和总帧数以计算视频时长
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 计算视频时长
        self.video_length = total_frames / fps
        print(f"Video length: {self.video_length} seconds")

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            h, w, _ = frame.shape
            original_ratio = w / h

            # 如果原视频的宽高比大于目标宽高比，说明原视频更“宽”
            if original_ratio > target_ratio:
                new_width = fixed_width
                new_height = int(fixed_width / original_ratio)
            else:  # 否则，原视频更“高”
                new_width = int(fixed_width * original_ratio / target_ratio)
                new_height = int(fixed_width / target_ratio)

            # 调整帧大小以匹配新的尺寸，同时保持原视频的比例
            frame_resized = cv2.resize(
                frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

            # 创建一个新的帧，用绿色填充作为背景
            background_frame = np.zeros(
                (int(fixed_width / target_ratio), fixed_width, 3), dtype=np.uint8)
            background_frame[:] = self.bg_color  # 设置为绿色背景

            # 将调整大小后的视频帧放置到背景帧中心位置
            y_offset = (background_frame.shape[0] - new_height) // 2
            x_offset = (background_frame.shape[1] - new_width) // 2

            background_frame[y_offset:y_offset + new_height,
                             x_offset:x_offset + new_width] = frame_resized

            # 显示处理后的帧
            cv2.imshow(self.window_name, background_frame)

            # 等待一段时间再显示下一帧，模拟视频播放速度
            if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
                break

        # 释放视频捕捉对象并关闭所有OpenCV窗口
        cap.release()
        cv2.destroyAllWindows()


class JuLiangBaiYing:
    def __init__(self):
        global data
        self.data = data
        print('JuLiangBaiYing')
        self.is_crawling = None
        self.driver = None
        self.loop_speak_card_index = 0
        self.user_data_dir = self.data['user_data_dir']
        self.profile_directory = self.data['profile_directory']
        self.ua_user = self.data["ua_user"]
        self.goods_url = "https://buyin.jinritemai.com/api/anchor/livepc/promotions_v2"

    def login(self, is_crawling=False):
        self.is_crawling = is_crawling
        self.chrome_options = Options()
        set_options(self)
        service = Service(executable_path=self.data["executable_path"])
        if self.is_crawling:
            driver = webdriver_wire.Chrome(
                service=service, options=self.chrome_options)
        else:
            driver = webdriver.Chrome(
                service=service, options=self.chrome_options)
        driver.set_window_size(1200, 780)
        driver.set_script_timeout(30)
        driver.get(self.data["url-juliangbaiying-login"])
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "index_module__title___b535e"))
        )
        driver.execute_script("window.open();")
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(self.data["url-juliangbaiying-control"])
        if self.is_crawling:
            try:
                is_success = False
                while True:
                    for request in driver.requests:
                        if self.goods_url in request.url:
                            if request.response.headers.get('Content-Encoding') == 'br':
                                good = un_brotli(request.response.body)[
                                    'data']['promotions']
                                self.data['goods'] = good
                                print(
                                    f"抓取商品请求成功")
                                with open("data.json", "w", encoding="utf-8") as file:
                                    json.dump(self.data, file,
                                              ensure_ascii=False, indent=4)
                                is_success = True
                                break
                    if is_success:
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                print("停止监听请求")
        print("巨量应用 加载成功")
        self.driver = driver
        return self

    def close(self):
        self.driver.quit()
        return self


    def download_goods_media(self):
        for item in range(len(self.data["goods"])):
            id = self.data["goods"][item]["promotion_id"]
            dir_path = Path(f"{self.data['videos_path']}/{id}")
            if dir_path.exists() and dir_path.is_dir():
                continue
            url = f"https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?id={id}"
            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(0.2)
            self.driver.execute_script("window.open();")
            time.sleep(0.2)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(0.2)
            self.driver.get(url)
            time.sleep(1)
            try:
                # 下载视频
                elements = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
                time.sleep(1)
                if elements:
                    video_src = elements.get_attribute("src")
                    DownloadFile.start(
                        video_src, self.data['videos_path']+f"/{id}/{id}.mp4")
            except Exception:
                # 下载图片
                elements = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, "index_module__item___ac928"))
                )
                for item1 in range(len(elements)):
                    img_src = elements[item1].get_attribute("src")
                    DownloadFile.start(
                        img_src, self.data['videos_path']+f"/{id}/{item1}.jpg")
            finally:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
        print("商品资料下载完成")
        return self


    def send_comment(self, comment):
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
            self.driver.execute_script(request)
            print("发布评论——脚本运行结束")
        except Exception as e:
            print(f"发布评论——发生了一个非预期的异常: {e}")
        return self


    def switch_card(self, promotion_id):
        request = f"""
            fetch('https://buyin.jinritemai.com/api/anchor/livepc/setcurrent?verifyFp=verify_m7q9579r_8gWGFJ0Q_bGZY_40ce_89y9_j24sL6TY5vxY&fp=verify_m7q9579r_8gWGFJ0Q_bGZY_40ce_89y9_j24sL6TY5vxY&msToken=hkcfl9bKA_bykhNFw2tR1yCANvPuw1XHQ4erPqJeN8-abNLXL_vvdJULE2bX1HrtTVKVEMxuX71Z0U_qXv2ylB1iELWJRBeY6f6yi6hDQGVWCY-ce8tJ6qYLsWecxl-rUXme2ZSJRl9Jhpkn9NNZK15mux517fZxAtWTR8zbym9C&a_bogus=m6s5h7XwQp8VepASmCppyArlA8DlrsWyEMTxSy1PSoKtG1FYn2pPDGhgJOLy49JRBWBrie-7MEuKbxdb%2FVp9hq9kFmhvSuiWT4IAV0mL8qqXGz48ErfwCwmNtJGbUcTEO5KbJI61AtmO2DOUEr3hUp5y9ATJsQipPrrbDBRGPoFv6F47MNqxuNtDiXFx-5I4kj%3D%3D', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded',
                }},
                body: 'promotion_id={promotion_id}&cancel=false',
                credentials: 'include', 
                }})
                .then(response => {{response.json();}})
                .then(data => console.log(data))
                .catch((error) => {{
                    console.error('Error:', error);
                }});
            """
        try:
            self.driver.execute_script(request)
            print(f"切换讲解卡: {promotion_id} ——脚本运行结束")
        except Exception as e:
            print(f"切换讲解卡: {promotion_id} ——发生了一个非预期的异常: {e}")
        return self

    def switch_card_async(self, promotion_id):
        x = Thread(target=self.switch_card, args=(promotion_id,))
        x.daemon = True
        x.start()
        return self

    def loop_speak_card_handler_async(self, goods, wait_time=5):
        x = Thread(target=self.loop_speak_card_handler,
                   args=(goods, wait_time,))
        x.daemon = True
        x.start()
        return self

    def loop_speak_card_handler(self, goods, wait_time=5):
        self.loop_speak_card_index = 0
        self.is_loop_speak_card = True
        length = len(goods)
        if length > 0 and goods:
            while self.is_loop_speak_card:
                promotion_id = goods[self.loop_speak_card_index]['promotion_id']
                self.switch_card_async(promotion_id)
                self.loop_speak_card_index += 1
                if self.loop_speak_card_index >= length:
                    self.loop_speak_card_index = 0
                time.sleep(wait_time+random.uniform(0, 0.5))
        return self

    def loop_speak_card_handler_pause(self):
        self.is_loop_speak_card == False
        return self

    def loop_speak_card_handler_start(self):
        self.is_loop_speak_card == True
        return self


class AISpeaker:
    def __init__(self):
        global data
        print('noiz_login')
        self.data = data
        self.is_crawling = None
        self.driver = None
        self.user_data_dir = ""
        self.profile_directory = ""
        # self.user_data_dir = self.data['user_data_dir']
        # self.profile_directory = self.data['profile_directory']
        self.ua_user = self.data["ua_user"]
        self.name = self.data['AI_name']
        self.password = self.data['AI_password']
        self.driver = self.login()

    def speak_text_async(self, text, voice_id):
        x = Thread(target=self.speak_text, args=(text, voice_id,))
        x.daemon = True
        x.start()
        return self

    def close(self):
        self.driver.quit()
        return self

    def speak_text(self, text, voice_id):
        request = f"""
            const formData = new FormData();
            formData.append('text','{text}') 
            formData.append('voice_id','{voice_id}')
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
                }});
                audio.play(); // 播放音频
                }})
            .catch(error => console.error('There was a problem with the fetch operation:', error));
        """
        try:
            self.driver.execute_script(request)
            print("ai语音——脚本运行结束")
        except Exception as e:
            print(f"ai语音——发生了一个非预期的异常: {e}")
        return self

    def speak_text_wait(self, text, voice_id):
        request = f"""
            window.isPlayEnd = false;
            const formData = new FormData();
            formData.append('text','{text}') 
            formData.append('voice_id','{voice_id}')
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
                        window.isPlayEnd = true;
                    }});
                    audio.play(); // 播放音频
                }})
            .catch(error => console.error('There was a problem with the fetch operation:', error));
        """
        try:
            self.driver.execute_script(request)
            wait_for_audio_completion(
                self.driver, "window.isPlayEnd;")
            print("ai语音——脚本运行结束")
        except Exception as e:
            print(f"ai语音——发生了一个非预期的异常: {e}")
        return self

    def login(self, is_crawling=False):
        self.is_crawling = is_crawling
        self.chrome_options = Options()
        set_options(self)
        service = Service(executable_path=self.data["executable_path"])
        if self.is_crawling:
            driver = webdriver_wire.Chrome(
                service=service, options=self.chrome_options)
        else:
            driver = webdriver.Chrome(
                service=service, options=self.chrome_options)
        driver.set_window_size(980, 680)
        driver.set_script_timeout(30)
        time.sleep(1)
        driver.get(self.data["ai_audio_url_login"])
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
            type_character(name, self.name)
            type_character(password, self.password)
            time.sleep(1)
            login.click()
            print("AI spearker 加载成功")
            self.driver = driver
        except Exception as e:
            print(f"登陆失败，发生了一个非预期的异常: {e}")
        return self


class DownloadFile:
    def __init_(self):
        self.type = None
        self.url = None
        self.save_path = None

    def start(self, url, save_path, type=""):
        self.type = type
        self.url = url
        self.save_path = save_path
        print(f'download file: {save_path}')
        # 确保保存目录存在，如果不存在则创建
        directory = os.path.dirname(self.save_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 发送HTTP GET请求
        response = requests.get(self.url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 将下载的内容写入文件
        with open(self.save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)


def type_character(element, text):
    element.send_keys(text)


def wait_for_audio_completion(driver, params, timeout=25):
    while (True):
        completed = driver.execute_script(
            f"return {params}")
        if completed or timeout == 0:
            print("音频播放完成")
            break
        # print("音频仍在播放...")
        time.sleep(1)
        timeout -= 1
        # print(f"等待音频播放-{timeout}")
    driver.execute_script(
        "window.isPlayEnd=false;")


def set_options(self):
    if self.user_data_dir != "" and self.profile_directory != "":
        self.chrome_options.add_argument(
            f"--user-data-dir={self.user_data_dir}")
        self.chrome_options.add_argument(
            f"--profile-directory={self.profile_directory}")
    self.chrome_options.add_argument(f"user-agent={self.ua_user}")
    self.chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    self.chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    self.chrome_options.add_experimental_option(
        "useAutomationExtension", False)
    self.chrome_options.add_argument("--disable-extensions")
    self.chrome_options.add_argument("--disable-infobars")


def un_brotli(compressed_data):
    try:
        # 解压Brotli压缩的数据
        decompressed_data = brotli.decompress(compressed_data)
        # 将解压后的字节转换为字符串，假设原始数据是UTF-8编码的文本
        str_data = decompressed_data.decode('utf-8')
        print("Decompressed string:", str_data)

        # 如果预期结果是JSON格式，可以进一步解析
        json_data = json.loads(str_data)
        return json_data
    except brotli.error as e:
        print(f"Failed to decompress Brotli data: {e}")
    except UnicodeDecodeError:
        print("Decompressed data is not valid UTF-8 encoded text.")
    except json.JSONDecodeError:
        print("Decompressed data is not valid JSON format.")
