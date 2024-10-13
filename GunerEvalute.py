from Evaluate import *


# guner 只有两类数据
def getGuner(file,index):
    nerdata = []
    with open(file, encoding="utf-8", mode="r") as f:
        temp = []
        lines = f.readlines()
        lines=lines[:index*2]
        for i in range(0, len(lines) - 1, 2):
            # print(i)
            temp.append(lines[i].strip('\n'))
            temp.append(lines[i + 1].strip('\n'))
            # print(temp)
            a, b = -1, -1
            for i in range(len(temp)):
                if "人物" in temp[i]:
                    a = i
                elif "官职" in temp[i]:
                    b = i
                else:
                    pass
            ner = [temp[a], temp[b]]
            nerdata.append(ner)
            temp.clear()
    # 调整一下位置，0 per 1 官职
    return nerdata

def get_predict_evaluate(slst,nlst):
    i=0
    predictions=[]
    for s,n in zip(slst,nlst):
        # print(i)
        # print(s)
        # print(len(s))
        # print(n)
        per = get_perenity_menzi(n[0])
        perbio = bio_tagging(s, per,type='per')
        # print(per)
        # print(perbio)
        ofi=get_ofi_enity_guner(n[1])
        ofibio=bio_tagging(s,ofi,type="ofi")
        prediction=merge_bio_tags2(perbio,ofibio)
        predictions.append(prediction)
        # print(prediction)
        # print('00000')
        i+=1
    return predictions

def get_evaluate_onefile(pfile,biofilo,index):
    nerlist = getGuner(pfile,index)
    print(len(nerlist))
    s, y_true = get_y_true(biofilo)
    s=s[:index]
    y_true=y_true[:index]
    y_pred = get_predict_evaluate(s, nerlist)
    s,y_true,y_pred=check_data(s,y_true,y_pred)
    #评估
    print("evaluate")
    print(f1_score(y_true, y_pred))
    print(classification_report(y_true, y_pred))
    print("====")

def get_evaluate_print(predictfiles,bios,dataindex):
    for pre,bio,index in zip(predictfiles,bios,dataindex):
        print(pre)
        print(bio)
        get_evaluate_onefile(pre,bio,index)


"""
用于mt5进行guner数据的评估
"""
#1从bio文件中取一下真实bio标签
floder='data/Han/dataset/'+'all_nochange'
trainbio=floder+"/trainbio.json"
valbio=floder+"/valbio.json"
testbio=floder+"/testbio.json"
biofiles=[trainbio,valbio,testbio]

# 2弄清楚guner数据的数量
gunerindex=[1846,300,200]

# 3 预测数据
trainpre=floder+"/mt5trainpre.txt"
valpre=floder+"/mt5valpre.txt"
testpre=floder+"/mt5testpre.txt"
predicts=[trainpre,valpre,testpre]

get_evaluate_print(predicts,biofiles,gunerindex)
