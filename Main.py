from Tools import *

with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# 切换讲解卡同时播放视频
def handler():
    # JuLiangBaiYing().loop_speak_card_handler(data['goods'], 5)
    isContinue = False
    goods = data['goods']
    ju_driver = JuLiangBaiYing()
    ju_driver.download_goods_media()
    loop_speak_card_index = 0
    wait_time = 2
    is_loop_speak_card = True
    length = len(goods)
    while True:
        if isContinue:
            continue
        
        if length > 0 and goods:
            while is_loop_speak_card:
                promotion_id = goods[loop_speak_card_index]['promotion_id']
                ju_driver.switch_card_async(promotion_id)
                video_path = f"./{data['videos_path']}/{promotion_id}/{promotion_id}.mp4"
                img_path = f"./{data['videos_path']}/{promotion_id}/"
                if os.path.exists(video_path):
                    PlayVideo().play(video_path)
                else:
                    PlayImg().play(img_path)    
                loop_speak_card_index += 1
                if loop_speak_card_index >= length:
                    loop_speak_card_index = 0
                time.sleep(wait_time+random.uniform(0, 0.5))
        time.sleep(data['t'])


if __name__ == "__main__":
    handler()
