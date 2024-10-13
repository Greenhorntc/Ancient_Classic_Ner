"""
使用荀子模型
荀子模型是基于千问微调得到
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
from DataTools import *

modelpath=r"C:\Users\28205\PycharmProjects\LLMs\models\Xunzi-Qwen-Chat"
tokenizer = AutoTokenizer.from_pretrained(modelpath, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(modelpath, device_map="auto", trust_remote_code=True).eval()
model.generation_config = GenerationConfig.from_pretrained(modelpath, trust_remote_code=True) # 可指定不同的生成长度、top_p等相关超参

promptfile="prompt/prompt.txt"
fewshotfile="prompt/fewshot.txt"


def ask_model_chatglm(nerdata):
    tempa=[]
    qtype=["per","loc","time"]
    for type in qtype:
        # prompt, second = read_prompt_chatglm(promptfile, model=type)
        # print(prompt)
        # print("==")
        # print(second)
        # fewshot = readfewshot(fewshotfile, prompt, model=type)
        # q原文，a标注好的ner句子，t是翻译，d是检索到的字典
        q, a, t, d = get_q_a_t_d(nerdata, qtype=type)
        if type=="per":
            prompt="你非常了解古籍中的人物\n"
            # sentence="输入句子为："+q+"\n 识别句子中的人物实体,不存在请回答无。"
            sentence="输入句子为："+q+"\n 句子中是否存在人物实体？\n 请回答有 或者 无，不要回答其他内容！"
            second = "那么句子中人物是？"
        elif type=="time":
            prompt = "你非常了解古籍中的时间\n"
            # sentence = "输入句子为：" + q + "\n 识别句子中的时间实体,不存在请回答无。"
            sentence="输入句子为："+q+"\n 句子中是否存在时间实体？\n 请回答有 或者 无，不要回答其他内容！"
            second = "那么句子中时间是？"
        else:
            prompt="你非常了解古籍中的地点\n"
            # sentence = "输入句子为：" + q + "\n 识别句子中的地点实体,不存在请回答无。"
            sentence="输入句子为："+q+"\n 句子中是否存在地点实体？\n 请回答有 或者 无，不要回答其他内容！"
            second = "那么句子中地点是？"
        dialogue =prompt+sentence
        response, history = model.chat(tokenizer, dialogue, history=None)
        print(dialogue)
        print(response)
        # print(history)
        if "有" in response :
            print("=====第二轮=====")
            print(second)
            response2, history2= model.chat(tokenizer, second, history=history,temperature=0.2,top_p=0.1)
            print(response2)
            print("=====end=======")
        #     # tempdic[type]=finalresult
        # else:
        #     # tempdic[type]="无"
        #     response2="无"
        # tempa.append([response2])
    # return tempa


def ask_model_xunzi(nerdata):
    qtype = ["per", "loc", "time"]
    ans=[]
    for type in qtype:
        q, a, t, d = get_q_a_t_d(nerdata, qtype=type)
        #加了提示反而效果下降
        # prompt="你是中国古籍方面的专家，非常善于解决命名体识别任务。\n"
        if type=="per":
            sentence = "识别句子中的人物实体,句子为:" + q + "\n 回答的格式为(实体1，实体2..)如不存在请直接回答无"
        elif type=="time":
            sentence = "识别句子中的时间实体,句子为:" + q + "\n 回答的格式为(实体1，实体2..)如不存在请直接回答无"
        else:
            sentence = "识别句子中的地点实体,句子为:" + q + "\n 回答的格式为(实体1，实体2..)如不存在请直接回答无"
        response, history = model.chat(tokenizer, sentence, history=None)
        ans.append([response])
    return ans

def ask_model_xunzi2(data):
    qtype = ["per", "loc", "time"]
    ans=[]
    for type in qtype:
        #加了提示反而效果下降
        # prompt="你是中国古籍方面的专家，非常善于解决命名体识别任务。\n"
        if type=="per":
            sentence = "识别句子中的人物实体.\n 句子为:" + data + "回答的格式为(实体1，实体2..)如不存在请直接回答无"
        elif type=="time":
            sentence = "识别句子中的时间实体.\n句子为:" + data + " 回答的格式为(实体1，实体2..)如不存在请直接回答无"
        else:
            sentence = "识别句子中的地点实体.\n句子为:" + data + " 回答的格式为(实体1，实体2..)如不存在请直接回答无"
        response, history = model.chat(tokenizer, sentence, history=None)
        # print(sentence)
        # print(response)
        ans.append([response])
    return ans

def ask_model_xunzi_enity(nerdata):
    q, a, t, d = get_q_a_t_d(nerdata, qtype="loc")
    sentence="命名体识别任务，识别句子所有的实体。\n 句子为："+q+"\n 回答的格式为(实体1，实体2..)如不存在请直接回答无"
    response, history = model.chat(tokenizer, sentence, history=None)
    # print(sentence)
    # print(response)
    return response

def ask_model_xunzi_enity2(nerdata):
    sentence="命名体识别任务，识别句子所有的实体。\n 句子为："+nerdata+"\n 回答的格式为(实体1，实体2..)如不存在请直接回答无"
    response, history = model.chat(tokenizer, sentence, history=None)
    # print(sentence)
    # print(response)
    return response

def ask_model_xunzi_enity_unlabeld(s,keyword):
    inputs="请提取以下文本中的{}名：".format(keyword)+s
    # sentence="命名体识别任务，识别句子中的{}实体。句子为：".format(keyword)+s+"\n 回答的格式为(实体1，实体2..)如不存在请直接回答无"
    response, history = model.chat(tokenizer, inputs, history=None,temperature=0.9)
    # print(inputs)
    # print(response)
    return response

def getallanswer(data):
    enity_with_type=[]
    enityall=[]
    for ner in data:
        ans=ask_model_xunzi(ner)
        enity_with_type.append(ans)
        ans2=ask_model_xunzi_enity(ner)
        enityall.append(ans2)
    return enity_with_type,enityall

# save result
def saveresult(reslults,savepath):
    with open(savepath,mode="w",encoding="utf-8") as f:
        for reslult in reslults:
            reslult=str(reslult)
            f.write(reslult+"\n")
    print(savepath+ " saved over")


def read_translate(datafile):
    translatelist=[]
    with open(datafile,encoding='utf-8') as f:
        lines=f.readlines()
        for line in lines:
            line.strip("\n")
            translatelist.append(line)
    return translatelist

def getenityby_translate(datalist):
    enity_with_type = []
    enityall = []
    for trans in datalist:
        ans = ask_model_xunzi2(trans)
        enity_with_type.append(ans)
        ans2 = ask_model_xunzi_enity2(trans)
        enityall.append(ans2)
    return enity_with_type, enityall

