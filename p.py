"""
Version: 1.0
Autor: 兰田 Lambert_work@163.com
Date: 2025-02-25 16:32:40
LastEditors: lambertlt lambert_Y_Y@163.com
LastEditTime: 2025-03-02 02:15:25
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
import cv2
import simpleaudio as sa
import os
import requests
import time
import re
import pickle
import pyautogui
import random
import requests
import json

import subprocess

# 替换为你的视频文件路径

url = [
    "https://v26.douyinvod.com/c6f0a75743e1b08661d4470fa975a866/67cbda78/video/tos/cn/tos-cn-v-2e5523/osA34Dzgg0UNFD9bCKLghXjhQpOfITytgEQCtg/?a=1128&ch=0&cr=0&dr=0&er=0&lr=all&cd=0%7C0%7C0%7C0&cv=1&br=1394&bt=1394&cs=0&ds=4&ft=OXXf~77JWH6BMATKrcr0PD1IN&mime_type=video_mp4&qs=0&rc=ODRnOTZkZmdkZGlpPDw2M0BpajNoO2g6Zms7bjQzNGY1M0AvY2JgNDQ1Ni4xL15jXzIvYSNobzAycjRnMi5gLS1kNDBzcw%3D%3D&btag=80010e00090000&cc=2a&cquery=101B&dy_q=1741409366&feature_id=f0150a16a324336cda5d6dd0b69ed299&l=20250308124926A7E1237FA23C4E9D6887&req_cdn_type=",
    "https://v26.douyinvod.com/c6f0a75743e1b08661d4470fa975a866/67cbda78/video/tos/cn/tos-cn-v-2e5523/osA34Dzgg0UNFD9bCKLghXjhQpOfITytgEQCtg/?a=1128&ch=0&cr=0&dr=0&er=0&lr=all&cd=0%7C0%7C0%7C0&cv=1&br=1394&bt=1394&cs=0&ds=4&ft=OXXf~77JWH6BMATKrcr0PD1IN&mime_type=video_mp4&qs=0&rc=ODRnOTZkZmdkZGlpPDw2M0BpajNoO2g6Zms7bjQzNGY1M0AvY2JgNDQ1Ni4xL15jXzIvYSNobzAycjRnMi5gLS1kNDBzcw%3D%3D&btag=80010e00090000&cc=2a&cquery=101B&dy_q=1741409366&feature_id=f0150a16a324336cda5d6dd0b69ed299&l=20250308124926A7E1237FA23C4E9D6887&req_cdn_type=",
]



# 视频URL
video_url = url[0]

audio = AudioSegment.from_file("videos/test.mp4", format="mp4")

# 将音频转换为 .wav 格式的数据（simpleaudio 支持的格式）
raw_data = audio.raw_data

# 使用 simpleaudio 播放音频
play_obj = sa.play_buffer(
    raw_data,
    num_channels=audio.channels,    # 音频通道数
    bytes_per_sample=audio.sample_width,  # 每样本字节数
    sample_rate=audio.frame_rate    # 采样率
)
input("按 Enter 键停止播放...")

# 停止播放
play_obj.stop()

# 等待播放完成
# play_obj.wait_done()


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


# download_file(url[0],'./videos/test.mp4')
# 使用VideoCapture类打开视频流
# cap = cv2.VideoCapture(video_url)

# while cap.isOpened():
#     # 获取帧
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # 显示结果帧
#     cv2.imshow("Video", frame)

#     # 按'q'键退出
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break
    
# # 释放资源
# cap.release()
# cv2.destroyAllWindows()
