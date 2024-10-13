import openai
import os
from typing import List, Iterable
from DataTools import *

def read(fp: str, n: int) -> Iterable[List[str]]:
    i = 0
    lines = []  # a buffer to cache lines
    with open(fp,encoding="utf-8") as f:
        for line in f:
            i += 1
            lines.append(line.strip())  # append a line
            if i >= n:
                yield lines
                # reset buffer
                i = 0
                lines.clear()
    # remaining lines
    if i > 0:
        yield lines
#返回per人名 loc 地理 time 时间
def readfewshot(file,prompt,model):
    temp=[]
    datagen=read(file,4)
    for data in datagen:
        q=data[0]
        t=data[1]
        d=data[2]
        d = eval(d)
        if model=="per":
            d=d["人物"]
        if model == "loc":
            d = d["地点"]
        if model == "time":
            d = d["时间"]
        a=data[3]
        question = dialogue_with_direct_prompt_trans_dic(q, t, d, prompt)
        answer=a
        temp.append([question,answer])
    if model=="per":
        return temp[0:4]
    if model=="loc":
        return temp[4:8]
    else:
        return temp[-4:]


def generate_text_with_fewshot(text,fewshot):
    Q1=fewshot[0][0]
    A1=fewshot[0][1]

    Q2 = fewshot[1][0]
    A2 = fewshot[1][1]

    Q3 = fewshot[2][0]
    A3= fewshot[2][1]
    #先用三组试试
    # Q4 = fewshot[3][0]
    # A4 = fewshot[3][1]

    key=""
    openai.api_key = os.getenv('OPENAI_KEY', key)
    openai.api_base = ""
    messages = [
        {"role": "system", "content": "你是一名精通中国文言文的专家,非常了解古籍。"},
        {"role": "user", "content": Q1},
        {"role": "assistant", "content": A1},

        {"role": "user", "content": Q2},
        {"role": "assistant", "content": A2},

        {"role": "user", "content": Q3},
        {"role": "assistant", "content":A3},

        # {"role": "user", "content": Q3},
        # {"role": "assistant", "content": A3},

        {"role": "user", "content": text},
    ]
    #
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=messages,
    #     temperature=1.0,
    # )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=1.0,
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    print("summary_result:\n", result)
    return messages,result

#使用单论对话
def generate_text(text):
    key=""
    openai.api_key = os.getenv('', key)
    openai.api_base = ""
    messages = [
        {"role": "system", "content": "你是一名精通中国文言文的专家,非常了解儒家经典《十三经》"},
        {"role": "user", "content": text},
    ]

    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=messages,
    #     temperature=1.0,
    # )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=1.0,
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print("summary_result:\n", result)
    return result

#拼接上一轮的答案，然后再进行二轮对话
def twostepquestion(messages,result,newq):
    step1={"role": "assistant", "content": result}
    messages.append(step1)
    step2={"role": "user", "content": newq}
    messages.append(step2)
    # print(messages)
    # # print(messages[11].content)
    key = ""
    openai.api_key = os.getenv('', key)
    openai.api_base = ""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1.0,
    )
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=step2,
    #     temperature=1.0,
    # )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print("summary_result:\n", result)
    return result


