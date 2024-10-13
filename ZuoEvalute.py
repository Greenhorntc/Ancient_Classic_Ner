import json
from Evaluate import *
#1从bio文件中取一下真实bio标签

dspath='data/processed/all_ner_aug_medium/zuo/'
#bio 标注
biofiles=[dspath+'trainbio.json',dspath+'valbio.json',dspath+'testbio.json']
#模型实际预测
predicts=[dspath+"mt5trainpre.txt",dspath+"mt5valpre.txt",dspath+"mt5testpre.txt"]


#2hantest里面的数据需要对其per loc time
#2.1 既然是per loc time 依次读k条数据然后合并
def get_ner(file,n):
    nerdata = []
    with open(file,encoding="utf-8",mode="r") as f:
        temp=[]
        lines=f.readlines()
        for i in range(len(lines)):
            temp.append(lines[i].strip('\n'))
            if len(temp)==n:
                # if len(temp)==1500:
                nerdata.append(temp)
                temp=[]
            else:
                pass
    return nerdata

def merge_bio_tags(per, loc,time):
    merged_tags = []
    for tag1, tag2 ,tag3 in zip(per,loc,time):
        if tag1 != 'O':
            merged_tags.append(tag1)
        elif tag2 != 'O':
            merged_tags.append(tag2)
        else:
            merged_tags.append(tag3)
    return merged_tags


def get_predict_evaluate(slst,nlst):
    i=0
    predictions=[]
    for s,n in zip(slst,nlst):
        # print(i)
        # print(s)
        # print(len(s))
        # print(n)
        per = get_perenity_menzi(n[0])
        perbio = bio_per_tagging(s, per)
        # print(per)
        # print(perbio)
        loc = get_locenity_menzi(n[1])
        locbio=bio_loc_tagging(s,loc)
        # print(loc)
        # print(locbio)
        time = get_time_enity_menzi(n[2])
        timebio=bio_time_tagging(s,time)
        # print(time)
        # print(timebio)
        prediction=merge_bio_tags(perbio,locbio,timebio)
        predictions.append(prediction)
        # print(prediction)
        # print('00000')
        i+=1
    return predictions


# 前一个ner是先全部输出任务，地理，时间。顺序进行，现在是按照 3个一条数据输出
def getner2(file):
    nerdata = []
    with open(file, encoding="utf-8", mode="r") as f:
        temp = []
        lines = f.readlines()
        for i in range(0,len(lines)-1,3):
            # print(i)
            temp.append(lines[i].strip('\n'))
            temp.append(lines[i+1].strip('\n'))
            temp.append(lines[i+2].strip('\n'))
            # print(temp)
            a,b,c=-1,-1,-1
            for i in range(len(temp)):
                if "人物" in temp[i]:
                    a=i
                elif "地理" in temp[i] or "地点" in temp[i]:
                    b=i
                elif "时间" in temp[i]:
                    c=i
                else:
                    pass
            ner=[temp[a],temp[b],temp[c]]
            nerdata.append(ner)
            temp.clear()
    # 调整一下位置，0 per 1loc 2 time
    return nerdata



def get_evaluate_onefile(pfile,biofilo):
    nerlist = getner2(pfile)
    s, y_true = get_y_true(biofilo)
    y_pred = get_predict_evaluate(s, nerlist)
    s,y_true,y_pred=check_data(s,y_true,y_pred)
    #评估
    print("evaluate")
    print(f1_score(y_true, y_pred))
    print(classification_report(y_true, y_pred))
    print("====")



def get_evaluate_print(predictfiles,bios):
    for pre,bio in zip(predictfiles,bios):
        print(pre)
        print(bio)
        get_evaluate_onefile(pre,bio)

get_evaluate_print(predicts,biofiles)



# nerlist=getner2(predicts[0])
# s,y_true=get_y_true(biofiles[0])
# y_pred=get_predict_evaluate(s,nerlist)



