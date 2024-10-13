"""
使用科大讯飞认知大模型试试
"""
from DataTools import *
from LLM.message import *
from sparkdesk_api.core import SparkAPI
import time

appid = "your id"  # 填写控制台中获取的 APPID 信息
api_secret = "your api"  # 填写控制台中获取的 APISecret 信息
api_key = "your key"  # 填写控制台中获取的 APIKey 信息


promptfile="LLM/prompt/prompt.txt"
fewshotfile="LLM/prompt/fewshot.txt"

sparkAPI = SparkAPI(
    app_id=appid,
    api_secret=api_secret,
    # 默认api接口版本为3.1，配置其他版本需要指定Version参数（2.1或者1.1）
    api_key=api_key,
    # version=2.1
)


def getText(role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    return jsoncon


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def add_fewshot(fewshot):
    Q1 = getText("user",fewshot[0][0])
    A1 = getText("assistant",fewshot[0][1])
    Q2 = getText("user", fewshot[1][0])
    A2 = getText("assistant", fewshot[1][1])
    Q3 = getText("user",fewshot[2][0])
    A3 = getText("assistant",fewshot[2][1])
    allfew=[Q1,A1,Q2,A2,Q3,A3]
    return allfew

def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text



#讯飞星火,组装输入 diagonal+fewshot
# api不存在system这个角色，需要将prompt加进去
def generate_text_with_fewshot_spark(text,fewshot):
    prompt="<sys>:你是一名精通中国文言文的专家,非常了解古籍。\n"
    friststage=prompt+text
    print(friststage)
    #暂未加入fewshot
    history=add_fewshot(fewshot)
    # print(input2)
    ans = sparkAPI.chat(friststage, history=history)
    first=[getText("user",friststage),getText("assistant",ans)]
    first=first+history
    return ans,first

def twostep_question_apark(second,first):
    # print(first)
    result = sparkAPI.chat(second, history=first)
    return result

def ask_model_spark(nerdata):
    tempa=[]
    qtype=["per","loc","time"]
    for type in qtype:
        prompt, second = read_prompt(promptfile, model=type)
        fewshot = readfewshot(fewshotfile, prompt, model=type)
        q, a, t, d = get_q_a_t_d(nerdata, qtype=type)
        dialogue = dialogue_with_direct_prompt_trans_dic(q, t, d, prompt)
        # print(dialogue)
        result,first=generate_text_with_fewshot_spark(dialogue,fewshot)
        time.sleep(0.5)
        print(result)
        #需要计算一下提问的长度
        alllength=getlength(first)+len(second)
        print(str(alllength))
        if "有" in result and alllength<=4096:
            print("=====第二轮=====")
            print(second)
            #组装一下会话历史
            finalresult = twostep_question_apark(second,first)
            print(finalresult)
            # tempdic[type]=finalresult
        else:
            # tempdic[type]="无"
            finalresult="无"
        tempa.append([finalresult])
    return tempa


def gettag_by_spark(datalist):
    all=[]
    for nerdata in datalist:
        ans=ask_model_spark(nerdata)
        all.append(ans)
    return all


# save result
def saveresult(reslults,savepath):
    with open(savepath,mode="w",encoding="utf-8") as f:
        for reslult in reslults:
            reslult=str(reslult)
            f.write(reslult+"\n")
    print(savepath+ " saved over")


