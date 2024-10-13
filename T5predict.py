from datasets import Dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration, TrainingArguments, Trainer,DataCollatorForSeq2Seq
import json

datasetlofder="data/Han/dataset/all_nochange/"

 #  2 原版mt5
model_path=r"C:\Users\28205\PycharmProjects\LLMs\models\mT5-Base"
tokenizer = T5Tokenizer.from_pretrained(model_path)
output_dir = "savedmodel/all_nochange"
best_model = output_dir+'/best'
#测试集合预测
def preprocess(filepath):
    with open(filepath, encoding="utf-8", mode='r') as file:
        data = [json.loads(line.strip()) for line in file]
    inputs = []
    titles = []
    for item in data:
        inputs.append(item["abst"])
        titles.append(item["title"])
    return inputs, titles

model = T5ForConditionalGeneration.from_pretrained(best_model).cuda()
def predict(sources, batch_size=8):
    model.eval()  # 将模型转换为评估模式
    kwargs = {"num_beams": 4,"max_new_tokens":512}
    outputs = []
    for start in (range(0, len(sources), batch_size)):
        batch = sources[start:start + batch_size]
        input_tensor = tokenizer(batch, return_tensors="pt", truncation=True, padding=True,max_length=512).input_ids.cuda()
        outputs.extend(model.generate(input_ids=input_tensor, **kwargs))
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)

trainpath=datasetlofder+'train.json'
devpath=datasetlofder+'val.json'
testpath=datasetlofder+'test.json'

paths=[trainpath,devpath,testpath]
namlist=[datasetlofder+"mt5trainpre.txt",datasetlofder+"mt5valpre.txt",datasetlofder+"mt5testpre.txt"]

for path ,name in zip(paths[1:],namlist[1:]):
    print("model start predict data")
    print(path)
    print(name)
    inputs,labels=preprocess(path)
    generations = predict(inputs)
    for pre, label in zip(generations, labels):
        print(pre)
        print(label)

    with open(file=name,mode="w",encoding="utf-8") as f:
        for pre in generations:
            f.write(pre)
            f.write("\n")
print("predict saved over")