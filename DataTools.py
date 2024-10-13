import re
import opencc
import json
import random
#读取原始文本
def read_raw(rawtxt):
    with open(file=rawtxt, encoding="utf-8") as f:
        lines = f.readlines()
        rawlist = []
        for line in lines:
            if line == "\n":
                pass
            else:
                rawlist.append(traditional_to_simplified(line))
        return rawlist
def get_guner_New(rawlist):
    dataall=[]
    for raw in rawlist:
        raw=raw.strip("\n")
        # 使用正则表达式匹配人名和官职实体
        pattern = r'{(.*?)}'
        matches = re.findall(pattern, raw)
        if len(matches)==0:
            tmp={}
        else:
            per=[word.strip("|PER") for word in matches if word.endswith("|PER")]
            book=[word.strip("|BOOK") for word in matches if word.endswith("|BOOK")]
            ofi=[word.strip("|OFI") for word in matches if word.endswith("|OFI")]
            infos = [per, book, ofi]
            tmp = {}
            for i in range(len(infos)):
                if len(infos[i]) != 0:
                    if i == 0:
                        tmp["人物"] = infos[i]
                    if i == 1:
                        tmp["书籍"] = infos[i]
                    if i == 2:
                        tmp["官职"] = infos[i]
        # 去掉 {} 标记
        text = re.sub(r'{([^}]*)}', r'\1', raw)
        # 去掉 |PER 和 |OFI 标记
        text = re.sub(r'\|PER|\|OFI|\|BOOK', '', text)
        nerdata = re.sub(r'{([^|]+)\|BOOK}', r'<book>\1</book>', raw)
        # 替换人名
        nerdata = re.sub(r'{([^|]+)\|PER}', r'<per>\1</per>', nerdata)
        nerdata = re.sub(r'{([^|]+)\|OFI}', r'<ofi>\1</ofi>', nerdata)
        # print(nerdata)
        dataall.append([raw, text, tmp,nerdata])

    return dataall

def get_New(lst):
    all=[]
    for data in lst:
        # 按空格分割文本
        words = data.split()
        # 提取时间类型的词汇
        time_words = [word for word in words if word.endswith("/t")]
        time_words=[word.strip("/t") for word in time_words]
        # 提取人物类型的词汇
        person_words = [word for word in words if word.endswith("/nr")]
        person_words = [word.strip("/nr") for word in person_words]
        # 提取地点的词汇
        loc_words = [word for word in words if word.endswith("/ns")]
        loc_words = [word.strip("/ns") for word in loc_words]
        # print("时间类型的词汇：", time_words)
        # print("人物类型的词汇：", person_words)
        # print("地点类型的词汇：", loc_words)
        infos=[time_words,person_words,loc_words]
        #存一下出现的实体类别及具体的实体
        tmp={}
        for i in range(len(infos)):
            if len(infos[i])!=0:
                if i==0:
                    tmp["时间"]=infos[i]
                if i==1:
                    tmp["人物"]=infos[i]
                if i==2:
                    tmp["地点"]=infos[i]
        # print(tmp)
        clean_text = re.sub(r"/[a-z]+", "", data)
        all.append([data,clean_text,tmp])
    return all

def read_prompt_early(file):
    with open(file,encoding="utf-8") as f:
        lines=f.readlines()
        firstep=lines[:7]
        per=lines[8:12]
        loc=lines[13:17]
        orgization=lines[18:22]
        time=lines[23:27]
        return [firstep,per,loc,orgization,time]

def get_chat_txt(datalst,prompt):
    for i in range(len(datalst)):
        ortxt = "A为：" + datalst[i][1]
        # ordocu = "句子的注疏为：" + pair[1] + "\n"
        prompt[0][2] = ortxt
        diagle = "".join(prompt[0])
        datalst[i].append(diagle)
    return datalst



def change_raw(datalist):
    for i in range(len(datalist)):
        #去掉空格，转换简体
        data=datalist[i][1].strip("\n")
        simplified_data=traditional_to_simplified(data)
        # 1:加入提示模板
        datalist[i][1]=simplified_data
        datalist[i][2]=convert_dict_values_to_simplified(datalist[i][2])
        text_without_space=simplified_data.replace(" ", "")
        datalist[i].append(text_without_space)
    return datalist

def get_handled_data(file):
    raw=read_raw(file)
    handed=get_New(raw)
    final=change_raw(handed)
    return final

def traditional_to_simplified(traditional_text):
    cc = opencc.OpenCC('t2s.json')  # 加载繁体字转简体字的配置文件
    simplified_text = cc.convert(traditional_text)
    return simplified_text

def convert_dict_values_to_simplified(dic):
    converted_dict = {}
    for key, values in dic.items():
        converted_values = []
        for value in values:
            simplified_value = traditional_to_simplified(value)
            converted_values.append(simplified_value)
        converted_dict[key] = converted_values
    return converted_dict

def get_handled_data_guner(file):
    raw=read_raw(file)
    #[raw, text, tmp,nerdata] 原文本，处理后文本，ner信息，做好标记的ner输出
    handed=get_guner_New(raw)
    #1 处理后的文本简体化
    for data in handed:
        data[1]=traditional_to_simplified(data[1])
        data[3]=traditional_to_simplified(data[3])
    return handed

def get_ner_type_guner(datalist):
    resultlist = []
    # 1:判断句子中的实体类型
    enitytypeinstruct = "命名体类型识别任务，输出句子中存在的实体类别官职，人物，书籍等。input："
    for data in datalist:
        typeq = enitytypeinstruct + data[1]
        typea = list(data[2].keys())
        if len(typea) == 0:
            typeans = "无"
        else:
            typeans = " ".join(typea)
        tempdic = {"content": typeq, "result": "output:" + typeans}

        resultlist.append(tempdic)
    return resultlist

def get_ner_guner(datalist):
    resultlist = []
    # 2：人名地名书籍
    nerinsturct = "命名体识别任务，识别句子中的人物实体，官职实体，书籍实体等。input:"
    for data in datalist:
        nerq = nerinsturct + data[1]
        # 4写入数据
        tempdic = {"content": nerq, "result": "output:" + data[3]}
        # print(tempdic)
        resultlist.append(tempdic)
    return resultlist


def get_fintuned_data_guner(datalist):
    data1=get_ner_type_guner(datalist)
    data2=get_ner_guner(datalist)
    result=data1+data2
    return result

def get_translate_task(datalist):
    resultlist = []
    translateinsutrct="文言文翻译任务，将文言文翻译为现代白话文。input:"
    for data in datalist:
        tranlateq=translateinsutrct+data[0]
        tranlatea="output:"+data[1]
        tempdic = {"content": tranlateq, "result": tranlatea}
        resultlist.append(tempdic)
    return resultlist

def readjson(filepath):
    with open(filepath,encoding="utf-8", mode='r') as file:
        data = [json.loads(line.strip()) for line in file]
    return data

def write_json(datalist,filename):
    # 将数据写入JSON文件
    with open(filename, encoding="utf-8",mode='w') as f:
        for item in datalist:
            json.dump(item, f,ensure_ascii=False)
            f.write('\n')

def ws_task(datalist):
    # 1:分词数据
    wordsegprompt1 = "分词任务是将句子中的词汇进行分割，通过@符号将下列句子进行分词。input："
    resultlist = []
    for data in datalist:
        content = wordsegprompt1 + data[3]
        answer = "output：" + data[1].replace(" ", "@")
        tempdic = {"content": content, "result": answer}
        # print(tempdic)
        resultlist.append(tempdic)
    return resultlist

def ner_type_task(datalist):
    resultlist = []
    # 2:判断句子中的实体类型
    enitytypeinstruct = "命名体类型识别任务，输出句子中存在的实体类别地点，人物，时间等。input："
    for data in datalist:
        typeq = enitytypeinstruct + data[3]
        typea = list(data[2].keys())
        if len(typea) == 0:
            typeans = "无"
        else:
            typeans = " ".join(typea)
        tempdic = {"content": typeq, "result": "output:" + typeans}
        resultlist.append(tempdic)
    return resultlist

def ner_task(datalist):
    resultlist = []
    # 3：人名地名
    nerinsturct = "命名体识别任务，识别句子中的地点实体，人名实体，时间实体等。input:"
    for data in datalist:
        nerq = nerinsturct + data[3]
        # 1 判断有没有实体
        if data[2] == {}:
            pass
        else:
            # 2遍历实体dic替换文本
            new_dict = {value: key for key, values in data[2].items() for value in values}
            # print(new_dict)
            enitys = list(new_dict.keys())
            for enity in enitys:
                tag = {"人物": ["<per>", "</per>"], "时间": ["<time>", "</time>"], "地点": ["<loc>", "</loc>"]}
                # 3获取tag标签
                singal = tag[new_dict[enity]]
                data[3] = data[3].replace(enity, singal[0] + enity + singal[1])
        # 4写入数据
        tempdic = {"content": nerq, "result": "output:" + data[3]}
        # print(tempdic)
        resultlist.append(tempdic)
    return resultlist

#从原始数据提取一部分作为测试集合
def select_data(datalst,n):
    trainner=[]
    testner=[]
    # 从0-数据集里面个数随机采样n个数据
    chosenindex = random.sample(range(0, len(datalst)), n)
    # chosenindex 是np array 不是普通的list元素 in 这样不一定能找到的
    for i in range(len(datalst)):
        if i in chosenindex:
            testner.append(datalst[i])
        else:
            trainner.append(datalst[i])
    print("train:"+str(len(trainner)))
    print("test"+str(len(testner)))
    return trainner,testner


def get_ortxt(dic):
    content=dic["content"]
    ans=dic["result"]
    #原始输出是input后，output后的句子
    qindex=content.index("input:")
    q = content[qindex + 6:]  # 取出@符号后面的内容
    # print(q)
    aindex = ans.index("output:")
    a = ans[aindex + 7:]  # 取出@符号后面的内容
    # print(a)
    return q,a

def get_q_a_t(dic):
    content = dic["content"]
    ans = dic["result"]
    # 原始输出是input后，output后的句子
    qindex = content.index("input:")
    q = content[qindex + 6:]  # 取出@符号后面的内容
    # print(q)
    aindex = ans.index("output:")
    a = ans[aindex + 7:]  # 取出@符号后面的内容
    # print(a)
    t=dic["tranlate"]
    return q, a,t

def get_q_a_t_d(dic,qtype):
    content = dic["content"]
    ans = dic["result"]
    # 原始输出是input后，output后的句子
    qindex = content.index("input:")
    q = content[qindex + 6:]  # 取出@符号后面的内容
    # print(q)
    aindex = ans.index("output:")
    a = ans[aindex + 7:]  # 取出@符号后面的内容
    # print(a)
    t=dic["tranlate"]

    if qtype=="per":
        d=dic["words"]["人物"]
    elif qtype=="loc":
        d=dic["words"]["地点"]
    else:
        d=dic["words"]["时间"]
    return q, a,t,d

def readNer(jsonfile):
    # 读取 JSON 文件
    with open(jsonfile, 'r', encoding='utf-8') as file:
        data = []
        for line in file.readlines():
            dic = json.loads(line)
            data.append(dic)
    return data

def dialogue_with_direct_prompt_trans_dic(txt,translate,dic,prompt):
    prompt[2] = "A:" + txt + "\n"
    prompt[3]="B:"+translate+"\n"
    prompt[4]="C:"+str(dic)+"\n"
    dialogle = "".join(prompt)
    return dialogle

def read_prompt(file,model):
    with open(file,encoding="utf-8") as f:
        lines=f.readlines()
        firstep=lines[:8]
        per = lines[9:12]
        per = "".join(per)
        loc = lines[13:16]
        loc = "".join(loc)
        time = lines[17:20]
        time= "".join(time)
        if model=="per":
            firstep[5]="请结合A，B和C的信息，识别B中是否存在人物实体。\n"
            return firstep,per
        elif model=="loc":
            firstep[5] = "请结合A，B和C的信息，识别B中是否存在地点实体。\n"
            firstep[6]="如果B中不存在任何地点实体则回答：无，如果存在请回答：有。\n"
            return firstep,loc
        else:
            firstep[5] = "请结合A，B和C的信息，识别B中是否存在时间实体。\n"
            firstep[6]="如果B中不存在任何时间实体则回答：无，如果存在请回答：有。\n"
            return firstep,time

def read_prompt_chatglm(file,model):
    with open(file,encoding="utf-8") as f:
        lines=f.readlines()
        firstep=lines[:8]
        per = lines[9]
        per = "".join(per)
        loc = lines[11]
        loc = "".join(loc)
        time = lines[13]
        time= "".join(time)
        if model=="per":
            firstep[5]="请结合A，B和C的信息，识别B中是否存在人物实体。\n"
            return firstep,per
        elif model=="loc":
            firstep[5] = "请结合A，B和C的信息，识别B中是否存在地点实体。\n"
            firstep[6]="如果B中不存在任何地点实体则回答：无，如果存在请回答：有。\n"
            return firstep,loc
        else:
            firstep[5] = "请结合A，B和C的信息，识别B中是否存在时间实体。\n"
            firstep[6]="如果B中不存在任何时间实体则回答：无，如果存在请回答：有。\n"
            return firstep,time



