from LLM.message import *
from DataTools import *
import random


#从原始数据提取一部分作为测试集合
def select_data(datalst,n):
    trainner=[]
    testner=[]
    # 从0-数据集里面个数随机采样n个数据
    chosenindex = random.sample(range(0, len(datalst)), n)
    # chosenindex 是np array 不是普通的list元素 in 这样不一定能找到的
    for i in range(len(datalst)):
        if i in chosenindex:
            trainner.append(datalst[i])

        else:
            testner.append(datalst[i])
    return trainner,testner

def handata_get(file):
    data=get_handled_data(file)
    hanner = ner_task(data)
    print(len(hanner))
    return hanner



def dialogue_with_direct_prompt(txt,prompt):
    prompt[2]="A:"+txt+"\n"
    dialogle = "".join(prompt)
    # print(dialogle)
    return dialogle


def dialogue_with_direct_prompt_trans(txt,translate,prompt):
    prompt[2] = "A:" + txt + "\n"
    prompt[3] = "B:" + translate + "\n"
    dialogle = "".join(prompt)
    # print(dialogle)
    return dialogle
#3  add promtp and ask gpt
#3.1:prompt1 不存在其他信息，直接对古文原文进行提问。
# promptfile="prompt/directprompt.txt"
promptfile="prompt/prompt.txt"
# prompt,second=read_prompt(promptfile,model="per")
# prompt,second=read_prompt(promptfile,model="loc")
# prompt,second=read_prompt(promptfile,model="time")

fewshotfile="prompt/fewshot.txt"
# fewshot=readfewshot(fewshotfile,prompt,model="per")
# fewshot=readfewshot(fewshotfile,prompt,model="loc")
# fewshot=readfewshot(fewshotfile,prompt,model="time")

# 3.2 conmbine data and prompt

def ask_model_all(nerdata):
    tempa=[]
    # qtype=["per","loc","time",'ofi','weapon'....]
    qtype=["per","loc","time"]
    for type in qtype:
        prompt, second = read_prompt(promptfile, model=type)
        fewshot = readfewshot(fewshotfile, prompt, model=type)
        q, a, t, d = get_q_a_t_d(nerdata, qtype=type)
        dialogue = dialogue_with_direct_prompt_trans_dic(q, t, d, prompt)
        # print(dialogue)
        firststepmessage, result = generate_text_with_fewshot(dialogue, fewshot)
        if "有" in result:
            # print("=====第二轮=====")
            finalresult = twostepquestion(firststepmessage, result, second)
            # print(a)
        else:
            finalresult="无"

        tempa.append(finalresult)
    return tempa
def gettag_ask_gpt(datalist):
    all=[]
    for nerdata in datalist:
        ans=ask_model_all(nerdata)
        all.append(ans)
    return all


# save result
def saveresult(reslults,savepath):
    with open(savepath,mode="w",encoding="utf-8") as f:
        for reslult in reslults:
            reslult=str(reslult)
            f.write(reslult+"\n")
    print(savepath+ " saved over")







