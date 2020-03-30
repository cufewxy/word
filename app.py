from tkinter import *
from tkinter import ttk
# import pandas as pd
from pandas import read_excel, concat
from collections import OrderedDict, Counter
import json
import os
import datetime
from tkinter import scrolledtext


# import numpy as np
# import xlrd


class Application(Frame):
    def __init__(self, master=None):
        # 数据定义
        self.word_data = None
        self.cur_word_list = None
        self.category_struct = OrderedDict()
        self.effect_text_variable = None
        self.word_id = None
        self.model = {}
        self.text_label = None
        self.word_text = None
        # 布局定义
        self.course_combox = None
        self.category_combox = None
        self.course_status_var = None
        self.cur_word_var = None
        self.course_progress_bar = None
        self.word_progress_bar = None
        self.only_foreign_radio = None
        self.only_chinese_radio = None
        # 用户目录定义
        self.course = None
        self.category = None
        # 读取数据
        self.load_word_data()
        self.load_setting()
        self.load_model()
        # 窗口区
        Frame.__init__(self, master)
        self.pack()
        self.window_init()
        self.create_layout()
        # 初始化
        self.update_category()
        self.get_word()
        self.click_btn_count = 0

    def load_word_data(self):
        """
        读取单词文件
        """
        self.word_data = None
        df = read_excel("word.xlsx", dtype=str, sheet_name=None)
        for key, value in df.items():
            value["course"] = key
            value["id"] = value["course"] + "_" + value["category"] + value["foreign"]
            value["row"] = range(len(value))
            self.word_data = concat((self.word_data, value))
        for c1, grouped in self.word_data.groupby("course"):
            category_list = grouped["category"].unique().tolist()
            category_list = [c for c in category_list]
            self.category_struct[c1] = category_list

    def load_setting(self):
        """
        读取设置
        """
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                setting = json.load(f)
                self.course = setting["course"]
                self.category = setting["category"]

    def save_setting(self):
        """
        更新设置
        """
        setting = {"course": self.course,
                   "category": self.category}
        with open("settings.json", "w") as f:
            json.dump(setting, f)

    def load_model(self):
        """
        读取模型
        """
        if os.path.exists("model.json"):
            with open("model.json", "r") as f:
                self.model = json.load(f)
        for key in self.word_data["id"]:
            if key not in self.model:
                self.model[key] = {
                    "total_count": 0, "forget_count": 0, "remember_count": 0,
                    "last_remember_time": datetime.datetime(year=2019, month=1, day=1).strftime("%Y%m%d%H%M%S"),
                    "last_time": datetime.datetime(year=2019, month=1, day=1).strftime("%Y%m%d%H%M%S"),
                    "last_choice": -1}

    def window_init(self):
        """
        初始化窗口
        """
        self.master.title('Word')
        self.master.geometry("240x360+1000+200")

    def create_layout(self):
        """
        创建布局
        """
        # 选择单词列表区
        frm1 = Frame(self)
        self.course_combox = ttk.Combobox(frm1, width=13)  # 初始化
        category_value_list = ["全部"] + list(self.category_struct.keys())
        self.course_combox["values"] = category_value_list
        try:
            if self.course is not None:
                self.course_combox.current(category_value_list.index(self.course))
        except ValueError:
            self.course_combox.current(0)
        self.course_combox.bind("<<ComboboxSelected>>", self.on_choose_course)
        self.course_combox.pack(side=LEFT)

        self.category_combox = ttk.Combobox(frm1, width=13)  # 初始化
        category_value_list = ["全部"]
        try:
            if self.category is not None and self.category != "全部":
                category_value_list.extend(self.category_struct[self.course])
            self.category_combox["values"] = category_value_list
            if self.category is not None:
                self.category_combox.current(category_value_list.index(self.category))
        except (ValueError, KeyError):
            self.category_combox["values"] = category_value_list
            self.category_combox.current(0)
        self.category_combox.bind("<<ComboboxSelected>>", self.on_choose_category)
        self.category_combox.pack(side=LEFT)
        frm1.pack()
        # 课程进度区
        frm2 = Frame(self)
        self.course_status_var = StringVar(frm2)
        self.course_progress_bar = ttk.Progressbar(frm2, orient="horizontal", length=90, mode="determinate")
        self.course_progress_bar["maximum"] = 100
        self.course_progress_bar["value"] = 20
        course_status_label = Label(frm2, textvariable=self.course_status_var, font=('Arial', 10), width=16,
                                    height=1)
        course_status_label.pack(side=LEFT)
        self.course_progress_bar.pack(side=LEFT)
        frm2.pack()

        # 单词进度区
        frm3 = Frame(self)
        self.cur_word_var = StringVar(frm3)
        self.word_progress_bar = ttk.Progressbar(frm3, orient="horizontal", length=90, mode="determinate")
        self.word_progress_bar["maximum"] = 100
        self.word_progress_bar["value"] = 20
        cur_word_label = Label(frm3, textvariable=self.cur_word_var, font=('Arial', 10), width=16, height=1)
        cur_word_label.pack(side=LEFT)
        self.word_progress_bar.pack(side=LEFT)
        frm3.pack()
        # 单词展示区
        frm4 = Frame(self)
        self.word_text = scrolledtext.ScrolledText(frm4, font=('Arial', 12), width=24, height=13)
        self.word_text.pack()
        frm4.pack()

        # 用户复选区
        frm5 = Frame(self)
        self.radio_choice = IntVar()
        self.all_radio = Radiobutton(frm5, text='全部', command=self.on_click_check, variable=self.radio_choice, value=0)
        self.only_foreign_radio = Radiobutton(frm5, text='仅外文', command=self.on_click_check, variable=self.radio_choice,
                                              value=1)
        self.only_chinese_radio = Radiobutton(frm5, text='仅中文', command=self.on_click_check, variable=self.radio_choice,
                                              value=2)
        self.all_radio.pack(side=LEFT)
        self.only_foreign_radio.pack(side=LEFT)
        self.only_chinese_radio.pack(side=LEFT)
        frm5.pack()
        # 用户按钮区
        frm6 = Frame(self)
        forget_btn = Button(frm6, text='不认识', width=10, height=1, command=lambda: self.on_click_btn(0))
        forget_btn.pack(side=LEFT)
        uncertain_btn = Button(frm6, text='不确定', width=10, height=1, command=lambda: self.on_click_btn(1))
        uncertain_btn.pack(side=LEFT)
        remember_btn = Button(frm6, text='认识', width=10, height=1, command=lambda: self.on_click_btn(2))
        remember_btn.pack(side=LEFT)
        frm6.pack()

    def on_choose_course(self, *args):
        """
        选择第一个目录后的动作，
        ①如果是选择"全部"，则不筛选，清除二级目录，记录到硬盘中最新选择，并直接返回单词
        ②如果是选择其他，则控制二级目录
        """
        value = self.course_combox.get()
        if value == "全部":
            self.course = "全部"
            self.category = "全部"
            self.category_combox["values"] = ["全部"]
            self.category_combox.current(0)
            self.save_setting()
            self.update_category()
            self.get_word()
        else:
            self.category_combox["values"] = ["全部"] + self.category_struct[value]
            self.category_combox.current(0)
            self.course = value

    def on_choose_category(self, *args):
        """
        选择第二个目录后的动作
        ①记录最新选择到硬盘
        ②返回单词
        """
        value = self.category_combox.get()
        self.category = value
        self.save_setting()
        self.update_category()
        self.get_word()

    def update_category(self):
        """
        根据目录更新当前单词
        """
        if self.course is None and self.category is None:  # 第一次运行时
            self.cur_word_list = self.word_data
        elif self.course == "全部":
            self.cur_word_list = self.word_data
        elif self.category == "全部":
            self.cur_word_list = self.word_data[self.word_data["course"] == self.course]
        else:
            self.cur_word_list = self.word_data[(self.word_data["course"] == self.course) & (
                    self.word_data["category"] == self.category)]

    @staticmethod
    def _ebbinghaus(x):
        """
        艾宾浩斯遗忘曲线
        """
        return 0.56 * (x / 3600) ** 0.06

    def _feedback_prob(self, word_id):
        """
        根据用户反馈得到单词记住的概率
        """
        total_count = self.model[word_id]["total_count"]
        forget_count = self.model[word_id]["forget_count"]
        remember_count = self.model[word_id]["remember_count"]
        last_choice = self.model[word_id]["last_choice"]
        uncertain_count = total_count - forget_count - remember_count
        if last_choice == -1:  # 单词未出现
            return -10
        elif last_choice == 0:
            return forget_count % 20 / 100  # forget对应0-20
        elif last_choice == 1:
            return (uncertain_count % 20 + 20) / 100  # uncertain 对应20-40
        else:
            if remember_count >= 5:
                return 0.99
            return (remember_count * 12 + 40) / 100

    def get_word(self):
        """
        根据模型，返回单词文本
        """
        # 1. 计算最新的遗忘度
        weight_dict = {}
        time_dict = {}
        feedback_prob_dict = {}
        last_choice_lst = []
        cur_word = set(self.cur_word_list["id"].tolist())
        for key, value in self.model.items():
            if key in cur_word:
                feedback_res = self._feedback_prob(key)
                feedback_forget_prob = 1 - feedback_res
                seconds = (datetime.datetime.now() - datetime.datetime.strptime(value["last_remember_time"],
                                                                                "%Y%m%d%H%M%S")).total_seconds()
                ebbinghaus_prob = self._ebbinghaus(seconds)
                weight_dict[key] = feedback_forget_prob * 0.8 + ebbinghaus_prob * 0.2
                feedback_prob_dict[key] = feedback_res
                time_dict[key] = value["last_time"]
                last_choice_lst.append(value["last_choice"])
        # 2. 根据权重找到单词，同时保证近期没有出现过
        weight_column = self.cur_word_list["id"].apply(lambda x: weight_dict[x] if x in weight_dict else 0.5)
        latest_id = [v[0] for v in
                     sorted(time_dict.items(), key=lambda x: x[1], reverse=True)[:int(len(cur_word) / 4)]]  # 最新的一半
        while 1:
            self.word_id, self.word_row = self.cur_word_list.sample(weights=weight_column)[["id", "row"]].values[0]
            if self.word_id not in latest_id or len(latest_id) >= len(self.cur_word_list) or len(latest_id) == 0:
                break

        # 3. 更新单词文本
        text = self.format_text(self.word_data[self.word_data["id"] == self.word_id])
        self.word_text.delete(1.0, END)
        self.word_text.insert("insert", text)

        # 4. 更新课程进度文本
        c = Counter(last_choice_lst)
        self.course_status_var.set(f"{c[-1]} {c[0]} {c[1]} {c[2]} {c[0] + c[1] + c[2] + c[-1]}")
        # self.course_progress_bar["value"] = np.mean(list(feedback_prob_dict.values())) * 100
        self.course_progress_bar["value"] = sum([max(v, 0) for v in list(feedback_prob_dict.values())]) / len(
            list(feedback_prob_dict.values())) * 100

        # 5. 更新单词进度文本
        self.cur_word_var.set(f"单词行 {self.word_row + 2}")
        self.word_progress_bar["value"] = feedback_prob_dict[self.word_id] * 100

    def format_text(self, word_line):
        """
        格式化输出
        choice: 0表示全部显示，1表示仅外文，2表示仅中文
        """
        word_line = word_line[["foreign", "kana", "meaning", "sentence", "notes"]].values.tolist()[0]
        res = ""
        choice = self.radio_choice.get()
        for i in range(len(word_line)):
            line = word_line[i]
            if isinstance(line, str):
                if choice == 0 or (choice == 1 and i == 0) or (choice == 2 and i >= 2):
                    res += line
                else:
                    res += "" * len(line)
                res += "\n\n\n"
        res = res[:-3]
        return res

    def _update_model(self, value):
        """
        更新模型
        """
        self.model[self.word_id]["last_time"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.model[self.word_id]["total_count"] += 1
        if value == 0:
            self.model[self.word_id]["forget_count"] += 1
        if value == 2:
            self.model[self.word_id]["remember_count"] += 1
            self.model[self.word_id]["last_remember_time"] = self.model[self.word_id]["last_time"]

        self.model[self.word_id]["last_choice"] = value

    def _save_model(self):
        """
        保存模型
        """
        with open("model.json", "w") as f:
            json.dump(self.model, f)

    def on_click_check(self):
        """
        用户点击单选框后，更新文本
        """
        text = self.format_text(self.word_data[self.word_data["id"] == self.word_id])
        self.word_text.delete(1.0, END)
        self.word_text.insert("insert", text)

    def on_click_btn(self, value):
        """
        用户点击按钮后，更新模型
        value是用户熟悉程度，0: 不认识, 1: 不确定, 2: 认识
        """
        self._update_model(value)
        self.get_word()
        self.click_btn_count += 1
        if self.click_btn_count % 10 == 0:
            self._save_model()
            self.load_word_data()
            self.update_category()


if __name__ == '__main__':
    app = Application()
    app.mainloop()
