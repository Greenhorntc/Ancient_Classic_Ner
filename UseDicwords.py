"""
使用十三经大辞典进行数据增强，提供额外的信息
"""
from DataTools import *
import pandas as pd
def readxls(filename):
    df=pd.read_excel(filename,sheet_name=None)
    return df

def getwords(df):
    sheet_data_dict = {}
    for sheet_name, sheet_data in df.items():
        # print("shetname is %s" % sheet_name)
        # print(sheet_data)
        sheet_data_dict[sheet_name] = sheet_data.values.tolist()
        # print("--------------------")

    for key in sheet_data_dict:
        wordsllist = sheet_data_dict[key]
        wordsllist = [x[1] for x in wordsllist]
        sheet_data_dict[key] = wordsllist
    # print(sheet_data_dict)
    return sheet_data_dict

def getwords_dic(filename):
    df=readxls(filename)
    wordsdic=getwords(df)
    return wordsdic

def get_dic(filename):
    result=[]
    datalist=readNer(filename)
    for data in datalist:
        q,a=get_ortxt(data)
        words=add_words(q)
        data["words"]=words
        result.append(data)
    return result

def add_words(text,dic):
    result = {}
    result["人物"]=[]
    result["地点"]=[]
    result["时间"]=[]
    # 检查句子中是否存在列表中的单词
    for word in dic["人物（F）"]:
        if word in text:
            result["人物"].append(word)
    for word in dic["地理 （F）"]:
        if word in text:
            result["地点"].append(word)
    for word in dic["天文（F）"]:
        if word in text:
            result["时间"].append(word)
    return result

#key 必须是十三经大辞典的key
def  filter_dic_words(s,dic,key):
    result = {}
    result[key[:-3]]=[]
    for word in dic[key]:
        if word in s:
            result[key[:-3]].append(word)

    return result
# 保存数据
def getdatasave(filename,savename,wordsdic):
    datalist=readjson(filename)
    for nerdata in datalist:
        q, a, t = get_q_a_t(nerdata)
        dic = add_words(q, wordsdic)
        nerdata["words"] = dic
    write_json(datalist,savename)
#单独存在一个txt中
def save_txt(filename,savename):
    result=[]
    datalist=readjson(filename)
    for nerdata in datalist:
        q, a, t = get_q_a_t(nerdata)
        dic = add_words(q, wordsdic)
        result.append(dic)
    write_json(result,savename)

if __name__=="__main__":
    dicfile = "data/十三经词典(已核对).xlsx"
    wordsdic = getwords_dic(dicfile)
    print("over")
