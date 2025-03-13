from Tools import *

with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# 切换讲解卡同时播放视频
def handler():
    # JuLiangBaiYing().loop_speak_card_handler(data['goods'], 5)
    isContinue = False
    goods = data['goods']
    ai_driver = AISpeaker()
    ju_driver = JuLiangBaiYing()
    ju_driver.download_goods_media()
    loop_speak_card_index = 0
    promotion_slogans_index = 0
    wait_time = 0
    is_loop_speak_card = True
    length = len(goods)
    while True:
        if isContinue:
            continue
        if length > 0 and goods:
            while is_loop_speak_card:
                random_float = random.uniform(0, 1)
                next = random.choice(["接下来这款", "下一款"])
                sale = random.choice(["是一个爆款", "是一个热销款"])
                hot = random.choice(["赶快冲它", "大家可以点开看看", "真的很合适"])
                sentence = ""
                promotion_id = goods[loop_speak_card_index]['promotion_id']
                if random_float > 0.5:
                    sentence = data['promotion_slogans'][promotion_slogans_index]
                    promotion_slogans_index += 1
                    if promotion_slogans_index >= len(data['promotion_slogans']):
                        promotion_slogans_index = 0
                if random_float > 0.7:
                    ju_driver.switch_card_async(promotion_id)
                    random.shuffle(data['live_interval_audio_list'])
                    ai_driver.speak_text_wait(
                        f"{random.choice(data['live_interval_audio_list'])}", f"{random.choice(data['voice_id'])}")
                ju_driver.switch_card_async(promotion_id)
                ai_driver.speak_text_wait(
                    f"{next} {sale}发卡：{goods[loop_speak_card_index]['elastic_title']},现在活动价,仅需{goods[loop_speak_card_index]['price_desc']['min_price']['integer']}.{goods[loop_speak_card_index]['price_desc']['min_price']['decimal']}元，在小黄车{loop_speak_card_index+1}号链接 {hot}！{sentence}", f"{random.choice(data['voice_id'])}")
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
