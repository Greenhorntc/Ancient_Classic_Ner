from DataTools import *
from UseDicwords import getwords_dic,add_words
import random
"""
用于处理Guner数据
"""

class Guner():
    def __init__(self,datafile,worddic):
        self.data=datafile
        self.datalist=get_handled_data_guner(datafile)
        self.nerdic=worddic

    def create_data_pair(self):
        self.datapair=[]
        for data in self.datalist:
            self.datapair.append([data[1],data[2]])
        return self.datapair
    def bio_ner_taggging(self,s,ners,type):
        if type=="人物":
            tag1='B-PER'
            tag2='I-PER'
        else:
            tag1 = 'B-OFI'
            tag2 = 'I-OFI'

        tagged_sentence = ['O'] * len(s)
        for entity in ners:
            start = 0
            while start < len(s):
                match = re.search(re.escape(entity), s[start:])
                if match:
                    start_index = match.start() + start
                    end_index = match.end() + start
                    tagged_sentence[start_index] = tag1
                    for i in range(start_index + 1, end_index):
                        tagged_sentence[i] = tag2
                    start = end_index
                else:
                    break
        return tagged_sentence

    def merge_bio(self,per,ofi):
        merged_tags = []
        for tag1, tag2 in zip(per, ofi):
            if tag1 != 'O':
                merged_tags.append(tag1)
            else:
                merged_tags.append(tag2)

        return merged_tags

    def data_aug_to_bio(self,data):
        cleaned_sentence = re.sub(r'\/[a-z]+', '', data[0])
        # 去除句子中间的空格
        sentence = cleaned_sentence.replace(' ', '')
        # 1 {}啥都没有
        if data[1]=={}:
            bio = ['O'] * len(sentence)
        else:
            # 把 没有的实体补齐好了
            # 2 只要两种实体 per和 ofi
            if "人物" not in data[1].keys():
                data[1]["人物"]=[]
            if "官职" not in data[1].keys():
                data[1]["官职"]=[]
            # 书籍实体不标注
            if "书籍" in data[1].keys():
                data[1].pop("书籍")
            perbio = self.bio_ner_taggging(sentence, data[1]["人物"], "人物")
            ofibio = self.bio_ner_taggging(sentence, data[1]["官职"], "官职")
            bio=self.merge_bio(perbio,ofibio)
            # print(data[1])
            # print(bio)
        a=len(sentence)
        b=len(bio)
        if a!=b:
            print("warnning")
            print(data)
            print(bio)
            print(a)
            print(b)
        return [sentence,data[1],bio]

    def getS_T_B(self):
        pairs=self.create_data_pair()
        stb=[]
        for pair in pairs:
            stb.append(self.data_aug_to_bio(pair))
        return stb

    def fix_dic(self, dic):
        newdic = {}
        for key, item in dic.items():
            less2 = [word for word in item if len(str(word)) >= 2]
            newdic[key] = less2
        return newdic

    def use_dic_to_create_stentce(self,s,givenner,d):
        # 修正十三经大辞典中少于2的词汇
        d=self.fix_dic(d)
        # 职官（F）
        perwords = d['人物（F）']
        ofiwords = d['职官（F）']
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
                else:
                    longwords = ofiwords
                    # 3 去对应的words里面找个长度一样的
                if lenw == 1:
                    templist.append([word, word])
                else:
                    # print("0000")
                    # print(lenw)
                    # print(word)
                    # print(longwords)
                    filtered_list = [ner for ner in longwords if len(ner) == lenw]
                    # print(filtered_list)
                    random_word = random.choice(filtered_list)
                    templist.append([word, random_word])
            for replacement in templist:
                old_word, new_word = replacement
                s = s.replace(old_word, new_word)
            outputner[key] = [x[1] for x in templist]
        return s, outputner


    def dataAug_pair(self,datalst,ntimes,type):
        createddata = []
        # 对于句子中全是一个词的句子，以及都是无的句子不应该进行复制
        for data in datalst:
            s=data[0]
            n=data[1]
            b=data[2]
            # 获取每个key对应的list，然后对list的元素长度进行统计
            condition = []
            for key in n:
                list = n[key]
                lentemp = [len(x) for x in list]
                condition.append(any(element > 1 for element in lentemp))
            # print(condition)
            createddata.append([s, n, b])
            # 句子里面的ner全是1的 就不增强了
            if len(condition) == 0 or True not in condition:
                pass
            else:
                if type == 'train':
                    for i in range(0, ntimes):
                        ouputs, outputn = self.use_dic_to_create_stentce(s, n, self.nerdic)
                        createddata.append([ouputs, outputn, b])
                else:
                    pass
        return createddata

    def get_sample(self,datalist, n):
        chosenindex1 = random.sample(range(0, len(datalist)), n)
        small = []
        big = []
        for i in range(len(datalist)):
            if i in chosenindex1:
                small.append(datalist[i])
            else:
                big.append(datalist[i])
        return small, big


# 得到的数据转换成dic形式，用于单独保存
    def change_data2_dic(self, lst):
        datalist = []
        for i in range(len(lst)):
            dic = {"id": i, "title": lst[i][1], "abst": lst[i][0]}
            datalist.append(dic)
        return datalist

    def write_json(self,datalist, filename):
        # 将数据写入JSON文件
        with open(filename, encoding="utf-8", mode='w') as f:
            for item in datalist:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        f.close()

    def save2_bio(self,data,name):
        datalist = []
        for i in data:
            # print(i)
            s = i[0]
            bio = i[2]
            dic = {"stentece": s, "bio": bio}
            datalist.append(dic)
        self.write_json(datalist, filename=name)
        print("write down")

    def guner_get_data(self,n1,n2,type):
        datalst = self.getS_T_B()
        print("Guner data used :{}".format(len(datalst)))
        # train val test
        notrain,train=self.get_sample(datalst,n1)
        val,test=self.get_sample(notrain,n2)
        print("Guner data train :{}".format(len(train)))
        print("Guner data val :{}".format(len(val)))
        print("Guner data test :{}".format(len(test)))
        if type=="aug":
            train = self.dataAug_pair(datalst=train,ntimes=2, type="train")
            print("Guner data train word replaced  :{}".format(len(train)))
        else:
            train=self.dataAug_pair(datalst=train,ntimes=0, type="train without aug")
            print("Guner data train no chagne  :{}".format(len(train)))
        return train,val,test

    def Guner_create_ds(self,savefolder,type="train"):
        train,val,test=self.guner_get_data(n1=500,n2=300,type=type)
        biosavepath=[x+"bio.json" for x in savefolder]
        self.save2_bio(train,name=biosavepath[0])
        self.save2_bio(val,name=biosavepath[1])
        self.save2_bio(test,name=biosavepath[2])

    def check_ner_None(self,dic):
        for value in dic.values():
            if value:  # 如果value不为空
                return False  # 返回原字典
        return True  # 如果所有value都为空，返回None

    def datapair_to_labeldata(self,datalist):
        # prompt1 = "识别人物实体，标记人类个体或具体人物姓名的实体。"
        # prompt2 = "识别地理实体，标记地理位置、地名或与地理相关的实体。"
        # prompt3 = "识别时间实体，标记时间、日期、年代或与时间相关的实体。"
        prompt1 = "识别句子中的人物实体，"
        prompt3 = "识别句子中的官职实体，"
        answer1 ='人物实体：无'
        answer3 ='官职实体：无'
        prompts=[prompt1,prompt3]
        answers=[answer1,answer3]
        datapair_final=[]
        for data in datalist:
            x=data[0]
            y=data[1]
            #第一种直接是无 {'人物': [], '官职': []}
            if self.check_ner_None(y):
                for prompt,answer in zip(prompts,answers):
                    strinput = prompt+'句子：' + x
                    pair = (strinput, answer)
                    datapair_final.append(pair)
            #第二种label中有实体
            else:
                keylist=list(y.keys())
                # 数据增强uie拿来的数据，所有的key都是3个。在这些数据中，只要因对空list，也就是无ner的清理。
                if len(keylist) == 2:
                    for key in y:
                        prompt = '识别句子中的' + key + "实体，"
                        sentence = prompt + '句子：' + x
                        ylist=list(set(y[key]))
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
        return datapair_final

if __name__=="__main__":

    # 加载十三经词典
    dicfile = "data/十三经词典(已核对).xlsx"
    wordsdic = getwords_dic(dicfile)
    #savefloder
    savedsfloder='data/processed/Guner/'
    dspath=[savedsfloder+'train',savedsfloder+'val',savedsfloder+'test']

    # 读取数据集
    file="data/Guner/GuNER2023_train.txt"
    gunerds=Guner(file,worddic=wordsdic)
    # gunertrain, gunerval, gunertest = gunerds.guner_get_data(n1=500, n2=300, type="aug")
    # gunertrainpair = gunerds.datapair_to_labeldata(gunertrain)
    gunerds.Guner_create_ds(savefolder=dspath,type="aug")
