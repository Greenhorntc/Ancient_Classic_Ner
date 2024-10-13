import openai
import os
import pandas as pd
import ast
#使用单论对话
def generate_text(prompt,text):
    key="yourkey"
    openai.api_key = os.getenv('OPENAI_KEY', key)
    openai.api_base = "openai or ohter website"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1.0,
    )
    #也可以使用gpt4
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=messages,
    #     temperature=1.0,
    # )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print("summary_result:\n", result)
    return result,messages

def two_step_dia(messages, result, newq):
    # 拼接上一轮的答案，然后再进行二轮对话
    step1 = {"role": "assistant", "content": result}
    messages.append(step1)
    step2 = {"role": "user", "content": newq}
    messages.append(step2)
    # print(messages)
    # # print(messages[11].content)
    key = "sk-yourkey"
    openai.api_key = os.getenv('OPENAI_KEY', key)
    openai.api_base = "openai or ohter website"
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


prompt1='给定以下实体类型[‘人物’，‘地理’，‘时间’,‘官职’]，阅读给定的句子并找出表示上述命名实体类型的所有单词/短语。以[“entity_type”、“entity_name”]格式回答，不带任何解释。如果不存在实体，则只需回答“[]”。"'

prompt2='你现在是一名精通古籍的专家，并且十分了解句子中的实体。给定以下实体类型[‘人物’,‘地理’,‘时间’,‘官职’]。句子中存在哪类实体？以列表[“entity_type1”,“entity_type2”]格式回答，不带任何解释。如果不存在实体，则只需回答无。'

filepath='your xlsx here'
df=pd.read_excel(filepath,sheet_name="Sheet1")
# print(df.head(5))
slst=df["句子"].tolist()

result=[]
for s in slst:
    ans=generate_text(prompt1,s)
    result.append(ans)
print(result)
df["实体"]=result

for s in slst:
    print(s)
    ans,message=generate_text(prompt2,s)
    if "人物" in ans:
        q2='请识别出句子中类型是"人物"的实体。按照元组形式回复，(实体名称1,实体名称2)...除此之外不要回答任何内容。'
        ans2=two_step_dia(message,ans,q2)

    if "地理" in ans:
        q2='请识别出句子中类型是"地理"的实体。按照元组形式回复，(实体名称1,实体名称2)...除此之外不要回答任何内容。'
        ans2=two_step_dia(message,ans,q2)

    if "时间" in ans:
        q2='请识别出句子中类型是"时间"的实体。按照元组形式回复，(实体名称1,实体名称2)...除此之外不要回答任何内容。'
        ans2=two_step_dia(message,ans,q2)

    if "无" in ans:
        ans2="无"
    else:
        print("第二轮对话结束")

