#用于构建进行fintuned的数据集
#使用的数据标记好的左传，数据格式{content，summery} 暂不涉及多轮对话
#0 转简体
from DataHandler import ZuoZhuan
from DataTools import *

def combine_data(datalist):
    ws=ws_task(datalist)
    nertype=ner_type_task(datalist)
    ner=ner_task(datalist)
    final=ws+nertype+ner
    print("ws"+str(len(ws)))
    print("nertype"+str(len(nertype)))
    print("ner"+str(len(ner)))
    return final

def guner_final(file):
    data=get_handled_data_guner(file)
    final=get_fintuned_data_guner(data)
    return final

def zuo_final(file):
    data=get_handled_data(file)
    final=combine_data(data)
    return final

def zuodata_get(file):
    data=get_handled_data(file)
    zuoner = ner_task(data)
    print(len(zuoner))

    return zuoner

print("start")

#文件位置 glod 处理成空格的文本
zuotrainfile="data/zuo/zuozhuan_train_utf8.txt"
zuodevfile="data/zuo/EvaHan_testa_gold.txt"
zuotestfile="data/zuo/EvaHan_testb_gold.txt"

#Other similar ancient Chinese  Book
gunertrian="data/Guner/GuNER2023_train.txt"
# gunertest="data/Guner/GuNER2023_test_public.txt"

#获取处理好的文本
#1 zuo
zuotrainfinal=zuo_final(zuotrainfile)
zuodevfinal=zuo_final(zuodevfile)
zuotestfinal=zuo_final(zuotestfile)

#guner
gunertrain=guner_final(gunertrian)
# gunertest=get_handled_data(gunertest)

#翻译任务
datafile="data/Zuo/四书五经.txt"
zuozhuan=ZuoZhuan(datafile)
zuodatalist=zuozhuan.get_content_pair()
zuodatalist=get_translate_task(zuodatalist)


alltrain=zuotrainfinal+gunertrain+zuodatalist
print("数据总量:"+str(len(alltrain)))
print("zuo:"+str(len(zuotrainfinal)))
print("guner:"+str(len(gunertrain)))
print("zuozhuan:"+str(len(zuodatalist)))
write_json(alltrain, "data/result/train.json")
write_json(zuodevfinal, "data/result/dev.json")
write_json(zuotestfinal, "data/result/test.json")


print("分任务数据集创建，并加入句子的翻译")
#2get data for chatgpt
#2.1 zuo
zuotrain=zuodata_get(zuotrainfile)
zuodev=zuodata_get(zuodevfile)
zuotest=zuodata_get(zuotestfile)
write_json(zuotrain, "data/result/ner/zuotrain.json")
write_json(zuodev, "data/result/ner/zuodev.json")
write_json(zuotest, "data/result/ner/zuotest.json")

#2.2guner
gunerdata=get_handled_data_guner(gunertrian)
guner=get_ner_guner(gunerdata)

#split train and test zuo and gunner
gunertrainn, gunertest=select_data(guner,n=200)
write_json(gunertrainn, "data/result/ner/gunertrain.json")
write_json(gunertest, "data/result/ner/gunertest.json")
print("over")


