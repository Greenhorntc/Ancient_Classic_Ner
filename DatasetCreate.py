from UseDicwords import getwords_dic
import re
import opencc
import json
import random
import ast
from datasets import Dataset
from Evaluate import bio_per_tagging,bio_loc_tagging,bio_time_tagging,merge_bio_tags,bio_tagging
from GuNerdataCreate import Guner

class DataSetCreate():
    def __init__(self,files,worddic):
        # files 0原始数据 1翻译 2词典 3篇章信息 4：大模型给的实体
        self.files=files
        #pamrm list 句子，ner实体，bio标注
        self.sentence,self.laberlnerlst,self.bio=self.getbio()
        self.nerdic=worddic

    #读取原始数据集合
    def read_raw(self,rawtxt):
        with open(file=rawtxt, encoding="utf-8") as f:
            lines = f.readlines()
            rawlist = []
            for line in lines:
                if line == "\n":
                    pass
                else:
                    rawlist.append(line)
            #提取数据的时候就将繁体字转换成简体
            return rawlist

    #读取json文件
    def readNer(self,jsonfile):
        # 读取 JSON 文件
        with open(jsonfile, 'r', encoding='utf-8') as file:
            data = []
            for line in file.readlines():
                dic = json.loads(line)
                data.append(dic)
        return data

    #简转繁体
    def traditional_to_simplified(self,traditional_text):
        cc = opencc.OpenCC('t2s.json')  # 加载繁体字转简体字的配置文件
        simplified_text = cc.convert(traditional_text)
        return simplified_text

    #原始句子转换成bio标注，测试时候使用
    def convert_to_bio(self,sentence):
        # 去除非中文标签
        sentence = re.sub(r'<[^>]+>', '', sentence)
        # 分词
        words = sentence.split(' ')
        # print("ooo")
        # print(words)
        # print(len(words))
        bio_tags = []
        for word in words:
            # print(word)
            if '/' in word:
                word, pos = word.split('/', 1)
                # print(word+pos)
                tag = "O"
                # if pos == 'nr':
                if  'nr' in pos :
                    tag = "B-PER"
                    bio_tags.extend([tag] + ["I-PER"] * (len(word) - 1))
                elif  'ns'in pos:
                    tag = "B-LOC"
                    bio_tags.extend([tag] + ["I-LOC"] * (len(word) - 1))
                elif 't' in pos:
                    tag = "B-TIME"
                    bio_tags.extend([tag] + ["I-TIME"] * (len(word) - 1))
                else:
                    bio_tags.extend(["O"] * len(word))
            # else:
            #     bio_tags.extend(["O"] * len(word))
            # print(bio_tags)
        return bio_tags

    def remove_special_tags(self,sentence):
        sentence = sentence.strip("\n")
        cleaned_sentence = re.sub(r'\/[a-z]+', '', sentence)
        # 去除句子中间的空格
        cleaned_sentence = cleaned_sentence.replace(' ', '')
        cleaned_sentence = cleaned_sentence.replace("\\", "")
        return cleaned_sentence

    def check_s_bio(self,sentence,nerlist,true):
        checks=[]
        checktag=[]
        checkner=[]
        for s,n, t in zip(sentence, nerlist,true):
            a = len(s)
            b = len(t)
            if a != b:
                print("Error SomeData not right")
                print(a)
                print(b)
                print(s)
                print(t)
            else:
                checks.append(s)
                checkner.append(n)
                checktag.append(t)
        return checks,checkner,checktag


    def getbio(self):
        # 用于进行实体标记的句子
        raw = self.read_raw(self.files[0])
        data = [self.traditional_to_simplified(x) for x in raw]
        # 用于进行实体标记的句子
        sentence = [self.remove_special_tags(x) for x in data]
        true = [self.convert_to_bio(x) for x in data]
        nerlst = self.get_answer_enity()
        #发现句子长度和bio标注长度对不上
        s,ner,t=self.check_s_bio(sentence,nerlst,true)
        return s, ner,t

    #2获得翻译好的文本 和 3篇章信息
    def getT_D_N_P(self,tfile):
        with open(file=tfile,mode="r",encoding="utf-8")as f:
            lines=f.readlines()
        lines=[x.strip("\n") for x in lines]
        return lines

    #4 潜在的的实体集合
    def get_related_enity(self,dicfile1,dicfile2,type):
        #1 先读取 两个dic文件
        word1=self.readNer(dicfile1)

        word2=self.getT_D_N_P(dicfile2)
        # 2处理其dic2中的其中
        word2=[self.get_ner_words(x) for x in word2]
        # print(len(worddiclist))
        # print(len(word2))
        # 3进行组合
        # print(word1)
        # print(word2)
        allwords=[]
        if type == "per":
            for dic1, lst2 in zip(word1, word2):
                temp=dic1["人物"]+lst2
                allwords.append(temp)

        elif type=="loc":
            for dic1, lst2 in zip(word1, word2):
                temp = dic1["地点"] + lst2
                allwords.append(temp)

        elif type=="time":
            for dic1, lst2 in zip(word1, word2):
                temp=dic1["时间"] + lst2
                allwords.append(temp)
        else:
            raise ValueError("输的什么！")
        # #再进行一次去重
        # allwords=list(set(allwords))
        result=[",".join(x) for x in allwords]
        return result

    #获取潜在的实体集合2，从翻译获取的句子
    def get_ner_words(self,line):
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')  # 匹配一个或多个中文字符的正则表达式
        chinese_phrases = re.findall(chinese_pattern, line)  # 提取中文词组
        #删除里面相同的词汇
        unique_data = list(set(chinese_phrases))
        # print(unique_data2)
        words_to_remove = ['人', '地点',"时间",'人名']
        # 去除指定词汇
        unique_data = [word for word in unique_data if word not in words_to_remove]
        return unique_data

    #原数据集已经标好的实体
    def get_answer_enity(self):
        lst=self.read_raw(self.files[0])
        lst = [self.traditional_to_simplified(x) for x in lst]
        all = []
        for data in lst:
            # 按空格分割文本
            words = data.split()
            # 提取时间类型的词汇
            time_words = [word for word in words if word.endswith("/t")]
            time_words = [word.strip("/t") for word in time_words]
            # 提取人物类型的词汇
            person_words = [word for word in words if word.endswith("/nr")]
            person_words = [word.strip("/nr") for word in person_words]
            # 提取地点的词汇
            loc_words = [word for word in words if word.endswith("/ns")]
            loc_words = [word.strip("/ns") for word in loc_words]
            # print("时间类型的词汇：", time_words)
            # print("人物类型的词汇：", person_words)
            # print("地点类型的词汇：", loc_words)
            infos = [time_words, person_words, loc_words]
            # 存一下出现的实体类别及具体的实体
            tmp = {}
            for i in range(len(infos)):
                if len(infos[i]) != 0:
                    if i == 0:
                        tmp["时间"] = infos[i]
                    if i == 1:
                        tmp["人物"] = infos[i]
                    if i == 2:
                        tmp["地点"] = infos[i]
            # print(tmp)
            all.append(tmp)
        return all


    def get_sentence_pair(self,sentence,t,n,ner,labeleddata,type):
        result=[]
        for orgrin,t,n,ner,ans in zip(sentence,t,n,ner,labeleddata):
            input1 = "原文："+orgrin+" 翻译：" + t+" 出处："+n+" 潜在的实体集合：("+ner+")"
            # print(input1)
            if type=="per":
                if len(ans)==0 or "人物" not in ans.keys():
                    answer="人物实体：无"
                else:
                    # if "人物" in ans.keys():
                    answer="人物实体：("+(",").join(ans["人物"])+")"
                #和DST任务一样，加入人物实体的解释。
                input=input1+"。人物实体指的是表示人类个体或具体人物姓名的实体。"
                pair=(input,answer)
                result.append(pair)

            elif type=="loc":
                if len(ans) == 0 or "地点" not in ans.keys():
                    answer = "地理实体：无"
                else:
                    answer = "地理实体：(" + (",").join(ans["地点"]) + ")"
                input = input1 + "。地理实体指的是表示地理位置、地名或与地理相关的实体。"
                pair = (input, answer)
                result.append(pair)

            else:
                if len(ans) == 0 or "时间" not in ans.keys():
                    answer = "时间实体：无"
                else:
                    answer = "时间实体：(" + (",").join(ans["时间"]) + ")"
                input = input1 + "。时间实体指的是表示时间、日期、年代或与时间相关的实体。"
                pair = (input, answer)
                result.append(pair)
        return result


    def combine_data(self):
        #1原始句子
        # self.sentence
        # #2句子翻译
        t=self.getT_D_N_P(self.files[1])
        # #3句子的出处
        n=self.getT_D_N_P(self.files[3])

        # 5获得标注的实体集合
        labeleddata = self.get_answer_enity()
        # print("====")
        # print(labeleddata)
        #4潜在的实体集合
        perner=self.get_related_enity(self.files[2],self.files[4],type="per")
        locner=self.get_related_enity(self.files[2],self.files[4],type="loc")
        timener=self.get_related_enity(self.files[2],self.files[4],type="time")
        #先是per
        perpair=self.get_sentence_pair(self.sentence,t,n,perner,labeleddata,type="per")
        locpair=self.get_sentence_pair(self.sentence,t,n,locner,labeleddata,type="loc")
        timepair=self.get_sentence_pair(self.sentence,t,n,timener,labeleddata,type="time")
        # print(len(perpair))
        # print(perpair[:100])
        # print("===")
        # print(locpair[:100])
        # print("====")
        # print(timepair[:100])
        allpair=perpair+locpair+timepair
        return allpair


    def save_data_2ndform(self,lst, name):

        sentences = lst[0]
        labels = lst[1]
        with open(name, mode="w", encoding="utf-8") as f:
            for sentence, label in zip(sentences, labels):
                # print(sentence)
                # print(label)
                for s, l in zip(sentence[0], label):
                    # print(s)
                    # print(l)
                    f.write(s + ' ' + l + '\n')
                f.write("\n")


    def write_json(self,datalist, filename):
        # 将数据写入JSON文件
        with open(filename, encoding="utf-8", mode='w') as f:
            for item in datalist:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        f.close()

    def create_ds(self,lst):
        labels = []
        txtfeature = []
        for i in range(len(lst)):
            txtfeature.append(lst[i][0])
            labels.append(lst[i][1])
        dic = {"features": txtfeature, "labels": labels}
        newds = Dataset.from_dict(dic)
        return newds

    def data_to_disk(self,ds, name):
        print(".....Data Save.......")
        path = name
        print(ds)
        ds.save_to_disk(path)
        print(".....Data has been Saved.......")

    def create_dataset(self,name):
        datapair = self.combine_data()
        print(len(datapair) / 3)
        dataset =self.create_data_dic(datapair)
        jsonname=name+".json"

        self.write_json(dataset, filename=jsonname)
        ds = self.create_ds(datapair)
        self.data_to_disk(ds,name)

        resultname=name+"bio.json"
        self.save_s_bio(name=resultname,data=datapair)

    def fix_dic(self,dic):
        newdic = {}
        for key, item in dic.items():
            less2 = [word for word in item if len(str(word)) >= 2]
            newdic[key] = less2
        return newdic

    def use_dic_to_create_stentce(self,s,givenner,d):
        d=self.fix_dic(d)
        # 职官（F）
        perwords = d['人物（F）']
        locwords = d['地理 （F）']
        timewords = d['天文（F）']
        # 1 去重
        outputner={}
        for key in givenner:
            # n[key] = list(set(n[key]))
            nerlist = list(set(givenner[key]))
            # 2遍历 这个list
            templist = []
            for word in nerlist:
                lenw = len(word)
                if key == '人物':
                    longwords = perwords
                elif key == '时间':
                    longwords = timewords
                else:
                    longwords = locwords
                    # 3 去对应的words里面找个长度一样的
                if lenw == 1:
                    templist.append([word, word])
                else:
                    filtered_list = [ner for ner in longwords if len(ner) == lenw]
                    random_word = random.choice(filtered_list)
                    templist.append([word, random_word])
            for replacement in templist:
                old_word, new_word = replacement
                s = s.replace(old_word, new_word)

            outputner[key] = [x[1] for x in templist]

        return s, outputner

    # 针对一条数据可以产生几条数据，原数据
    def get_data_augmentation_pair(self,ntimes,model):
        nerlst = self.laberlnerlst
        print(len(nerlst))
        stence=self.sentence
        bio=self.bio

        createddata=[]
        #对于句子中全是一个词的句子，以及都是无的句子不应该进行复制
        for s,n,b in zip(stence,nerlst,bio):
            # 获取每个key对应的list，然后对list的元素长度进行统计
            condition=[]
            for key in n:
                nerlist=list(set(n[key]))
                lentemp=[len(x) for x in nerlist]
                condition.append(any(element > 1 for element in lentemp))
            # print(condition)
            createddata.append([s, n, b])
            if len(condition)==0 or True not in condition:
                pass
            else:
                if model==True:
                    for i in range(0, ntimes):
                        ouputs, outputn = self.use_dic_to_create_stentce(s, n, self.nerdic)
                        createddata.append([ouputs,outputn,b])
                else:
                    pass
        return createddata
    #data 0 -s 1-n

    # 暂时只提供四种bio标记,后续还会添加
    def bio_tagging(self,sentence, ners, type):
        type_tag = {'per': ['B-PER', 'I-PER'], "time": ["B-TIME", "I-TIME"], "loc": ["B-LOC", "I-LOC"],
                    "ofi": ["B-OFI", "I-OFI"]}
        tag = type_tag[type]
        # 去除空格
        sentence = sentence.replace(' ', '')
        # 构建实体标注结果
        tagged_sentence = ['O'] * len(sentence)
        for entity in ners:
            start = 0
            while start < len(sentence):
                match = re.search(re.escape(entity), sentence[start:])
                if match:
                    start_index = match.start() + start
                    end_index = match.end() + start
                    tagged_sentence[start_index] = tag[0]
                    for i in range(start_index + 1, end_index):
                        tagged_sentence[i] = tag[1]
                    start = end_index
                else:
                    break
        return tagged_sentence

    def data_aug_to_bio(self,data):
        perbio = bio_tagging(data[0], data[1]['人物'],type="per")
        locbio = bio_tagging(data[0], data[1]['地点'],type="loc")
        timebio = bio_tagging(data[0], data[1]['时间'],type='time')
        ofibio = bio_tagging(data[0],data[1]['官职'],type='ofi')
        bio=merge_bio_tags(perbio,locbio,timebio,ofibio)
        a = len(data[0])
        b = len(bio)
        if a != b:
            print("warning len not qual")
            print(data)
            print(bio)
            print(a)
            print(b)
            print("================")
        return bio

    # def data_aug_to_bio(self,data):
    #     perbio=bio_per_tagging(data[0],data[1]['人物'])
    #     locbio=bio_loc_tagging(data[0],data[1]['地点'])
    #     timebio=bio_time_tagging(data[0],data[1]['时间'])
    #
    #     bio=merge_bio_tags(perbio,locbio,timebio)
    #     a=len(data[0])
    #     b=len(bio)
    #     if a!=b:
    #         print(data)
    #         print(bio)
    #         print(a)
    #         print(b)
    #     return bio

    def aug_data_select(self,aug_data_file):
        augdata = []
        with open(aug_data_file, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if line == '\n':
                    pass
                else:
                    line = line.strip("\n")
                    datalist = ast.literal_eval(line)
                    s = datalist[0]
                    s = s.replace(' ', '')
                    # nerdata=datalist[4]
                    nerdata = datalist[-1]
                    bio = self.data_aug_to_bio([s, nerdata])
                    augdata.append([s, nerdata, bio])


        num_elements = 5000  # 需要抽取的元素数量
        random_elements = random.sample(augdata, num_elements)
        print("aug len: " + str(len(random_elements)))
        return random_elements

    def data_aug_combin_data(self,aug_data_file,replace=True,aug=True):
        #0读取左传增强的数据,model参数控制了进入是否增强数据。
        # 第二次修改，使用词汇替换由一个参数控制，是否引入额外数据 也是使用另外惨呼
        replacener=self.get_data_augmentation_pair(ntimes=2,model=replace)

        print("replacener len: "+str(len(replacener)))
        # 选用增强数据
        if aug:
            augdata=self.aug_data_select(aug_data_file)

            print("augdata len: " + str(len(augdata)))
        else:
            augdata=[]
        return [replacener,augdata]
        # return augdata


    def datapair_to_labeldata(self,datalist):
        # prompt1 = "识别人物实体，标记人类个体或具体人物姓名的实体。"
        # prompt2 = "识别地理实体，标记地理位置、地名或与地理相关的实体。"
        # prompt3 = "识别时间实体，标记时间、日期、年代或与时间相关的实体。"
        prompt1 = "识别句子中的人物实体，"
        prompt2 = "识别句子中的地理实体，"
        prompt3 = "识别句子中的时间实体，"
        answer1 ='人物实体：无'
        answer2 ='地理实体：无'
        answer3 ='时间实体：无'
        prompts=[prompt1,prompt2,prompt3]
        answers=[answer1,answer2,answer3]
        datapair_final=[]
        for data in datalist:
            x=data[0]
            y=data[1]
            #第一种直接是无
            if y=='无':
                for prompt,answer in zip(prompts,answers):
                    strinput = prompt+'句子：' + x
                    pair = (strinput, answer)
                    datapair_final.append(pair)
            #第二种label中实体
            else:
                keylist=list(y.keys())
                # 数据增强uie拿来的数据，所有的key都是3个。在这些数据中，只要因对空list，也就是无ner的清理。
                if len(keylist) == 3:
                    for key in y:
                        prompt = '识别句子中的' + key + "实体，"
                        sentence = prompt + '句子：' + x
                        ylist=y[key]
                        if len(ylist)==0:
                            label=key+'实体：无'
                            pair = (sentence, label)
                            datapair_final.append(pair)
                        else:
                            # "人物实体：(" + (",").join(ans["人物"]) + ")"
                            label= key+"实体：(" + (",").join(ylist) + ")"
                            pair=(sentence,label)
                            datapair_final.append(pair)
                    # 针对原始左传有的key有，有的无
                else:
                    if '人物' not in y.keys():
                        sentence = prompt1 + '句子：' + x
                        pair=(sentence, answer1)
                        datapair_final.append(pair)
                    else:
                        pass
                    if '地点'not in y.keys():
                        sentence = prompt2 + '句子：' + x
                        pair = (sentence, answer2)
                        datapair_final.append(pair)
                    else:
                        pass

                    if "时间" not in y.keys():
                        sentence = prompt3 + '句子：' + x
                        pair = (sentence, answer3)
                        datapair_final.append(pair)
                    else:
                        pass
                    for key in y:
                        ylist = y[key]
                        prompt = '识别句子中的' + key + "实体，"
                        sentence = prompt + '句子：' + x
                        label = key + "实体：(" + (",").join(ylist)+')'
                        pair = (sentence, label)
                        datapair_final.append(pair)
        return datapair_final

    def save_ds_dic_json(self,final_data_pair,name):
        # 1 先存Dataset
        ds = self.create_ds(final_data_pair)
        self.data_to_disk(ds, name)
        print(final_data_pair)
        #2 保存为json
        data = self.create_data_dic(final_data_pair)
        jsonname = name + ".json"
        self.write_json(data, filename=jsonname)
        print('saved over')
    #直接输入数据对
    def create_dataaug_dataset(self, datapair,name):
        final_data_pair=self.datapair_to_labeldata(datapair)
        resultname = name + "bio.json"
        self.save_ds_dic_json(final_data_pair,name)

        self.save_s_bio(name=resultname,data=datapair)

    # 得到的数据转换成dic形式，用于单独保存
    def create_data_dic(self, lst):
        datalist = []
        for i in range(len(lst)):
            dic = {"id": i, "title": lst[i][1], "abst": lst[i][0]}
            datalist.append(dic)
        return datalist

    # 讲原始句子和 bio标签保存到结果中供后续评估
    def save_s_bio(self, data, name):
        name = name + 'bio.json'
        datalist = []
        for i in data:
            # print(i)
            s = i[0]
            bio = i[2]
            dic = {"stentece": s, "bio": bio}
            datalist.append(dic)
        self.write_json(datalist, filename=name)

#如果是采用大的数据集随机进行抽和划分，则从splitdata中取数据
s='data/zuo/splitdata/sentece_'
sfiles=[s+"train.txt",s+"dev.txt",s+"test.txt"]
t='data/zuo/splitdata/translate_'
tfiles=[t+"train.txt",t+"dev.txt",t+"test.txt"]
n='data/zuo/splitdata/passagename_'
nfiles=[n+"train.txt",n+"dev.txt",n+"test.txt"]
e1='data/zuo/splitdata/e1_'
e1files=[e1+"train.json",e1+"dev.json",e1+"test.json"]
e2='data/zuo/splitdata/e2_'
e2files=[e2+"train.txt",e2+"dev.txt",e2+"test.txt"]

dicfile = "data/十三经词典(已核对).xlsx"
wordsdic = getwords_dic(dicfile)

"""
针对两个数据集提供了两份蒸馏数据进行增强，修改5000/10000/15000可以获得不同数量的蒸馏数据
dataaugfile分别对应不同的数据集
"""
# dataaugfile='data/data_augmentation/STN/merged/zuo_aug.txt'
dataaugfile='data/data_augmentation/STN/merged/gunner_aug.txt'

# train dev test
train_2=[sfiles[0],tfiles[0],e1files[0],nfiles[0],e2files[0]]
dev_2=[sfiles[1],tfiles[1],e1files[1],nfiles[1],e2files[1]]
test_2=[sfiles[2],tfiles[2],e1files[2],nfiles[2],e2files[2]]


"""
part 6
加上实体替换,加入数据增强，replace=True,aug=Tru控制是否加入替换和蒸馏
"""
#1加载guner数据集
gunerfile="data/Guner/GuNER2023_train.txt"
gunerds=Guner(gunerfile,worddic=wordsdic)
# guner train 4998
gunertrain,gunerval,gunertest=gunerds.guner_get_data(n1=500,n2=300,type="aug")
gunertrainpair=gunerds.datapair_to_labeldata(gunertrain)
gunervalpair=gunerds.datapair_to_labeldata(gunerval)
gunertestpair=gunerds.datapair_to_labeldata(gunertest)



#1加载zuo 和蒸馏数据
zuotrainds=DataSetCreate(files=train_2,worddic=wordsdic)
zuotrain,aug=zuotrainds.data_aug_combin_data(aug_data_file=dataaugfile,replace=True,aug=True)
zuotrainpair=zuotrainds.datapair_to_labeldata(zuotrain)

#val
zuodev=DataSetCreate(files=dev_2,worddic=wordsdic)
zuodevdata,_=zuodev.data_aug_combin_data(aug_data_file=dataaugfile,replace=False,aug=False)
zuodevpair=zuodev.datapair_to_labeldata(zuodevdata)

#test
zuotest=DataSetCreate(files=test_2,worddic=wordsdic)
zuotestdata,_=zuotest.data_aug_combin_data(aug_data_file=dataaugfile,replace=False,aug=False)
zuotestpair=zuotest.datapair_to_labeldata(zuotestdata)

#2 aug
augpair=zuotrainds.datapair_to_labeldata(aug)

"""分别保存3个数据集，zuo，guner，all"""
zuo=[zuotrainpair+augpair,zuodevpair,zuotestpair]
guner=[gunertrainpair+augpair,gunervalpair,gunertestpair]
alldata=[zuotrainpair+gunertrainpair+augpair,zuodevpair+gunervalpair,zuotestpair+gunertestpair]

zuobio=[zuotrain+aug,zuodevdata,zuotestdata]
gunerbio=[gunertrain+aug,gunerval,gunertest]
alldatabio=[zuotrain+aug+gunertrain+aug,zuodevdata+gunerval,zuotestdata+gunertest]

dsnames=['zuo','guner','all']
savedsfloder='data/processed/all_ner_aug_medium/'
savedsfloders=[savedsfloder+x+'/' for x in dsnames]


def ds_deal(savedsfloder,datalst,bios):
    dspaths = [savedsfloder + 'train', savedsfloder + 'val', savedsfloder + 'test']
    for dspath,data,bio in zip(dspaths,datalst,bios):
        # '都行'zuotrainds valds
        zuotrainds.save_ds_dic_json(data, dspath)
        zuotrainds.save_s_bio(bio,dspath)

ds_deal(savedsfloders[0],zuo,zuobio)
ds_deal(savedsfloders[1],guner,gunerbio)
ds_deal(savedsfloders[2],alldata,alldatabio)

