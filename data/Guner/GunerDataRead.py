from DataTools import  *
from collections import Counter
import re



datafile="GuNER2023_train.txt"
hanfile=r"D:/PythonPro/ClassicDigital/data/Han/zuozhuan_train_utf8.txt"
augfile=r"D:/PythonPro/ClassicDigital/data/Han/dataset/final/train.json"
"""
转换成了左传格式，并改成了简体

[raw, text, ner,changedtxt] 原文本，处理后文本，ner信息，做好标记的ner输    
"""
guner=get_handled_data_guner(datafile)
zuo=get_handled_data(hanfile)
"""
统计数据集信息
1：per book offi
"""
# 统计该数据集的实体数量
def data_statistics(datalist):
    temp=[]
    sentence=0
    for data in datalist:
        lens=len(data[1])
        sentence+=lens
        print(data[1])
        print(data[2])
        temp.append(data[2])
    print("字数："+str(sentence))
    all=0
    counter = Counter()
    for dic in temp:
        for key, value in dic.items():
            # print(key)
            # print(value)
            # print(len(value))
            all+=len(value)
            counter[key] += len(value)
    print(all)
    print(counter)

# data_statistics(guner)
# data_statistics(zuo)

def ner_statistics(answer):

    a=0
    if "无" in answer:
       return a
    else:
        pattern = r"\((.*?)\)"  # 匹配括号内的内容
        matches = re.findall(pattern, answer)
        if matches:
            entities = matches[0].split(",")
            a=len(entities)
        else:
            a=0
    return a
perall=0
locall=0
timeall=0
augdata=readjson(augfile)[84891:]
for i in range(0,len(augdata),3):
    # print(augdata[i]["title"])
    per=ner_statistics(augdata[i]["title"])
    # print(augdata[i+1]["title"])
    loc=ner_statistics(augdata[i+1]["title"])
    # print(augdata[i+2]["title"])
    time=ner_statistics(augdata[i+2]["title"])
    perall+=per
    locall+=loc
    timeall+=time
    # print('......')

nerall=perall+locall+timeall
print("all {}".format(nerall)+" perall {}".format(perall)+"timeall: {} ".format(timeall)+" locall:{}".format(locall))
