from tkinter import Tk, Label, Button, Entry, StringVar, font
from Tools import *
from seleniumwire import webdriver

"""
功能点：
1. 定时切换讲解卡
2. 定时发布带节奏评论刷屏
3. 定时使用AI语音带节奏讲话
"""


class Controller:
    def __init__(self, data_path):
        with open(data_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

        self.index = 0
        self.root = Tk()
        self.root.geometry('900x400')
        self.root.title("直播助手操作程序")
        default_font = font.Font(family="微软雅黑", size=10)

        self.is_alone_loop_card = False
        self.is_live_assistant = False
        self.alone_t = StringVar(value=3)
        self.alone_t.trace_add('write', self.on_alone_t_changed)

        # 卡密
        self.label5 = Label(self.root, text="请输入激活码:", font=default_font)
        self.label5.grid(row=0, column=0, padx=15, pady=10, sticky='e')
        self.entry_var5 = StringVar()
        self.entry5 = Entry(
            self.root, textvariable=self.entry_var5, font=default_font)
        self.entry5.grid(row=0, column=1, padx=15, pady=10, sticky='w')

        # 开启直播助手伴侣
        self.label0 = Label(self.root, text="开启直播助手:", font=default_font)
        self.label0.grid(row=1, column=0, padx=15, pady=10, sticky='e')
        self.switch_var0 = StringVar(value="关闭")
        self.switch_button0 = Button(
            self.root, textvariable=self.switch_var0, command=self.start_juliangbaiying, font=default_font, width=8)
        self.switch_button0.grid(row=1, column=1, padx=15, pady=10, sticky='w')

        # 单独循环讲解卡开关
        self.label1 = Label(self.root, text="单独循环讲解卡开关:", font=default_font)
        self.label1.grid(row=2, column=0, padx=15, pady=10, sticky='e')
        self.switch_var = StringVar(value="关闭")
        self.switch_button1 = Button(
            self.root, textvariable=self.switch_var, command=self.alone_jump_card_btn, font=default_font, width=8)
        self.switch_button1.grid(row=2, column=1, padx=15, pady=10, sticky='w')
        self.label4 = Label(self.root, text="循环时间间隔(s):", font=default_font)
        self.label4.grid(row=2, column=2, padx=15, pady=10, sticky='e')
        self.entry_var = StringVar()
        self.entry = Entry(
            self.root, textvariable=self.alone_t, font=default_font)
        self.entry.grid(row=2, column=3, padx=15, pady=10, sticky='w')

        # 输入参数
        self.label2 = Label(self.root, text="输入参数:", font=default_font)
        self.label2.grid(row=3, column=0, padx=15, pady=10, sticky='e')
        self.entry_var1 = StringVar()
        self.entry1 = Entry(
            self.root, textvariable=self.entry_var1, font=default_font)
        self.entry1.grid(row=3, column=1, padx=15, pady=10, sticky='w')

        # 另一个输入
        self.label3 = Label(self.root, text="另一个输入:", font=default_font)
        self.label3.grid(row=4, column=0, padx=15, pady=10, sticky='e')
        self.entry_var2 = StringVar()
        self.entry2 = Entry(
            self.root, textvariable=self.entry_var2, font=default_font)
        self.entry2.grid(row=4, column=1, padx=15, pady=10, sticky='w')

    def on_alone_t_changed(self, *args):
        """当alone_t的值发生变化时调用"""
        new_value = self.alone_t.get()
        try:
            # 尝试将新值转换为浮点数以确认它是有效的数字
            float_new_value = float(new_value)
            if float_new_value <= 0:
                print("错误: 循环时间间隔必须大于0秒")
            else:
                print(f"循环时间间隔已更新为: {new_value}秒")
        except ValueError:
            print("错误: 请输入一个有效的数字作为循环时间间隔")

    def start_juliangbaiying(self):
        self.is_live_assistant = not self.is_live_assistant
        self.switch_var0.set("开启" if self.is_live_assistant else "关闭")

    def alone_jump_card_btn(self):
        """单独跳讲解卡"""
        self.is_alone_loop_card = not self.is_alone_loop_card
        self.switch_var.set("开启" if self.is_alone_loop_card else "关闭")
        JuLiangBaiYing().loop_speak_card_handler(
            data['goods'], self.alone_t)

    def jump(self):
        print(f"jump{self.index}")
        self.index += 1

    def handler(self):
        while True:
            if self.is_alone_loop_card:
                self.jump()
            time.sleep(self.data.get('t', 1))  # 默认值为1秒以防data['t']不存在

    def create_window(self):
        self.root.mainloop()

    def start_thread(self):
        thread = Thread(target=self.handler, daemon=True)
        thread.start()


if __name__ == "__main__":
    # controller = Controller("data.json")
    # controller.start_thread()
    # controller.create_window()

    JuLiangBaiYing().login(True)
    # driver.close()
