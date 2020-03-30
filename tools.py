"""
小工具，用于错误修复
"""
import os
import json
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


def check_duplicate():
    """
    用于所有课程间的单词重复检查
    """
    df_dict = pd.read_excel("word.xlsx", dtype=str, sheet_name=None)
    df = pd.DataFrame()

    for sheet, _df in df_dict.items():
        _df["course"] = sheet
        _df["row"] = np.arange(len(_df)) + 2
        df = pd.concat((df, _df))
    df.sort_values(by="foreign", inplace=True)
    print(df[df.duplicated("foreign", keep=False)][
              ["row", "course", "foreign", "kana", "meaning"]].reset_index(drop=True))


def pop_model_redundant_word():
    """
    Excel更新后，模型相应单词应该删掉
    """
    df_dict = pd.read_excel("word.xlsx", dtype=str, sheet_name=None)
    exist_words = []
    for sheet, _df in df_dict.items():
        exist_words.extend((sheet + "_" + _df["category"] + _df["foreign"]).tolist())

    if os.path.exists("model.json"):
        with open("model.json", "r") as f:
            model = json.load(f)
        duplicate_words = set(model.keys()) - set(exist_words)
        for word in duplicate_words:
            model.pop(word)
        with open("model.json", "w") as f:
            json.dump(model, f)



if __name__ == '__main__':
    check_duplicate()
    pop_model_redundant_word()
