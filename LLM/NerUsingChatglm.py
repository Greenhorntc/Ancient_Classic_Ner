import os
from DataHandler import Bookinfor
from transformers import AutoTokenizer, AutoModel
from DataTools import *
from LLM.message import readfewshot

def getText(role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    return jsoncon

def add_fewshot(fewshot):

    Q1 = getText("user",fewshot[0][0])
    A1 = getText("assistant",fewshot[0][1])
    Q2 = getText("user", fewshot[1][0])
    A2 = getText("assistant", fewshot[1][1])
    Q3 = getText("user",fewshot[2][0])
    A3 = getText("assistant",fewshot[2][1])
    allfew=[Q1,A1,Q2,A2,Q3,A3]

    # str=fewshot[0][0]+fewshot[0][1]+fewshot[1][0]+fewshot[1][1]+fewshot[2][0]+fewshot[2][1]
    # print(str)
    return allfew



promptfile="llm/prompt/prompt-chatglm.txt"
fewshotfile="llm/prompt/fewshot.txt"

modelpath=r"C:\Users\28205\PycharmProjects\LLMs\models\chatglm3-6b"
tokenizer = AutoTokenizer.from_pretrained(modelpath, trust_remote_code=True)
model = AutoModel.from_pretrained(modelpath, trust_remote_code=True, device='cuda')
model = model.eval()

def generate_text_with_fewshot_chatglm(dialogue,fewshot):
    # message=[]
    # system_info = {"role": "system", "content": "你是一名精通中国文言文的专家,非常了解儒家经典《十三经》\n"}
    prompt="<|system|>\n 你是一名精通中国文言文的专家,非常善于解决古籍的ner任务》\n "
    dialogue=prompt+dialogue
    print(dialogue)
    # message.append(system_info)
    # alldialogue=prompt+dialogue
    # all=prompt+add_fewshot(fewshot)+dialogue
    # history = add_fewshot(fewshot)
    # history.insert(0, system_info)
    # print(history)
    # print(dialogue)
    #先不加入fewshot，直接prompt然后输出
    response,history= model.chat(tokenizer, dialogue, history=[],temperature=0.2,top_p=0.1)
    return response,history

def ask_model_chatglm(nerdata):
    tempa=[]
    # qtype=["per","loc","time"]
    qtype=["per"]
    for type in qtype:
        prompt, second = read_prompt_chatglm(promptfile, model=type)
        fewshot = readfewshot(fewshotfile, prompt, model=type)
        q, a, t, d = get_q_a_t_d(nerdata, qtype=type)
        dialogue = dialogue_with_direct_prompt_trans_dic(q, t, d, prompt)
        result,history=generate_text_with_fewshot_chatglm(dialogue,fewshot)
        print("======")
        print(result)
        print(history)
        print("=== e n d ===")
    #     #需要计算一下提问的长度
    #     alllength=getlength(first)+len(second)
    #     print(str(alllength))
    #     if "有" in result and alllength<=4096:
        if "有" in result :
            print("=====第二轮=====")
            second="<|user|>\n 请回答，在输入B中找到的人物实体"
            print(second)
            response2, history2= model.chat(tokenizer, second, history=history,temperature=0.2,top_p=0.1)
            print(response2)
            # tempdic[type]=finalresult
        else:
            # tempdic[type]="无"
            response2="无"
        tempa.append([response2])
    return tempa
