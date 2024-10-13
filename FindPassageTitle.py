from DataHandler import Bookinfor
import os
from DataTools import *
#把txt全找出来
def read_text_files(folder_path):
    text_files = []  # 存储最底层目录下的文本文件路径列表
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)  # 构建文件路径
            if file.endswith(".txt"):  # 判断文件是否为文本文件
                text_files.append(file_path)
    return text_files

def changetext(str):
    # 删除标点符号和空格
    clean_text = re.sub(r'[^\u4e00-\u9fa5]+', '', str)
    return clean_text

def get_passage_name(name):
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')  # 匹配中文字符的正则表达式
    chinese_text = ''.join(re.findall(chinese_pattern, name))  # 提取中文字符
    return chinese_text


#每次读取文件太浪费时间，直接一次性读取，并按key vaule存储
def get_all_files(floder):
    bookdic={}
    text_files = read_text_files(floder)
    for text_file in text_files:
        with open(text_file,encoding="utf-8")as f:
            content=f.read()
            content=changetext(content)
            bookdic[text_file]=content
    return bookdic


def get_picked_files(sentence,bookdic):
    sentence=changetext(sentence)
    # print(text_files)
    #查找sentence所在的
    target_files = []  # 存储包含 "fbi" 字段的文件路径列表\
    for key in bookdic:
        content=bookdic[key]
        if sentence in content:
            target_files.append(key)
    target_files=[get_passage_name(x) for x in target_files]
    return target_files
# #读取训练集
# hantrain="data/result/nerwithdic/hantrain.json"
# handev="data/result/nerwithdic/handev.json"
# hantest="data/result/nerwithdic/hantest.json"
# hantrain=readjson(hantrain)
# handev=readjson(handev)
# hantest=readjson(hantest)

datafolder = "data/classicordata/"
bookdic=get_all_files(datafolder)
# print(bookdic.keys())
for key in bookdic.keys():
    print(key)

def get_connected_title_train(passagenamelst):
    #先看有没有匹配到结果
    #1 训练集和dev 两个都取自左传，所以只要匹配到左传字符直接输出就好了
    result=["无"]
    if len(passagenamelst)!=0 :
        for title in passagenamelst:
            if "左传" in title:
                result=[title]
    else:
        result=["无"]
    return result

def get_connected_title_test(lst):
    # 2 在测试集的话，不一定是左传，但还是优先左传title
    result = ["无"]
    if len(lst) != 0:
        for title in lst:
            if "左传" in title:
                result = [title]
            else:
                result = random.sample(lst, 1)
    #返回的titlelist是空的，没找到任何相关的
    else:
        result = ["无"]
    return result


# passagetityle=[]
# for nerdata in hantest[500:700]:
#     q, a, t, d = get_q_a_t_d(nerdata, qtype="per")
#     files=get_picked_files(q,bookdic)
#     files=get_connected_title_train(files)
#     # files=get_connected_title_test(files)
#     # print(files)

def get_title_saved(dic,name,model):
    all=[]
    for data in dic:
        q, a, t, d = get_q_a_t_d(data, qtype="per")
        files = get_picked_files(q, bookdic)
        if model=="train"or model=="dev":
            files=get_connected_title_train(files)
        else:
            files=get_connected_title_test(files)
        all.append(files[0])
    with open(file=name,mode="w",encoding="utf-8") as f:
        for filename in all:
            f.write(filename+"\n")
    print(name+" over ")

# flodername="data/Han/titlename/"
# train=flodername+"train.txt"
# dev=flodername+"dev.txt"
# test=flodername+"test.txt"
# get_title_saved(hantrain,train,model="train")
# get_title_saved(handev,dev,model="dev")
# get_title_saved(hantest,test,model="test")

# #获取文本位置
# rawfloder="data/rawtxt/"
# rawfiles=os.listdir(rawfloder)
# rawfiles=[rawfloder+x for x in rawfiles]
# print(rawfiles)

#易经
"""
['data/rawtxt/01周易正义.txt', 'data/rawtxt/02尚书正义.txt', 
'data/rawtxt/03毛诗正义.txt', 'data/rawtxt/04周礼注疏.txt', 
'data/rawtxt/05仪礼注疏.txt', 'data/rawtxt/06礼记正义.txt', 
'data/rawtxt/07春秋左传正义.txt', 'data/rawtxt/08春秋公羊传注疏.txt', 
'data/rawtxt/09春秋穀梁传注疏.txt', 'data/rawtxt/10孝经注疏.txt', 
'data/rawtxt/11尔雅注疏.txt', 'data/rawtxt/12论语注疏.txt',
 'data/rawtxt/13孟子注疏.txt']
尔雅 和 周礼 两书 论语 孟子无目录，需要另行处理
"""
# book=Bookinfor(rawfiles[6])
# txt=book.splitrawtxt()
# print(txt)
# chapterdic=book.chapter
# print(book.chapter.keys())
#获得文本对
# pair=book.pair_text_and_comment(chaptername="卷三 隐三年，尽五年")
# print(pair)
#pair 0 原文，1 注疏
# print(pair[0])
# print(pair[1])



#获取一下原始数据 train 和 dev 都是左传原文，所以可以直接从左传里面取
# def get_passage_chapter(sentence):
#
#     sentence = changetext(sentence)
#     print(sentence)
#     target=[]
#     chapterdic = list(book.chapter.keys())
#     for data in chapterdic:
#         text=book.pair_text_and_comment(data)
#         passagetext="".join(tuple(text[0]))
#         passagetext=changetext(passagetext)
#         print(passagetext)
#         if sentence in passagetext:
#             print(passagetext)
#             print(sentence)
#             target.append(data)
#         else:
#             pass
#     return target
#
