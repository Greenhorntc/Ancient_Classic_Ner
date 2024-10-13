from datasets import Dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration, TrainingArguments, Trainer,DataCollatorForSeq2Seq
import json

#0 加载数据集,
# all zuo guner ...
dspath='data/processed/all_ner_aug_medium/zuo/'

trainpath=dspath+'train'
valpath=dspath+"val"

train = Dataset.load_from_disk(trainpath).shuffle(seed=42)
val = Dataset.load_from_disk(valpath).shuffle(seed=42)
print(train)
print(val)


#1 mengzi
##model_path=r"C:\Users\28205\PycharmProjects\LLMs\models\mengzi-t5-base"

# 2 原版mt5
model_path=r"C:\Users\28205\PycharmProjects\LLMs\models\mT5-Base"
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)
data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer,model=model)

#处理数据 padding true  max_length: int = 512
def tokenize_fun(example):
    #原始features保留的同时，转换成inputids 和attention mask
    model_inputs = tokenizer(example["features"], max_length=512, truncation=True,padding=True,return_tensors="pt")
    #预测的标签tokeize转换后ids，然后放到inputs 中的labels中去
    labels = tokenizer(example["labels"], max_length=128, truncation=True,padding=True,return_tensors="pt")
    model_inputs["labels"] = labels["input_ids"]

    if "token_type_ids" in model_inputs:
        del model_inputs["token_type_ids"]

    return model_inputs

train_tokenized_ds = train.map(tokenize_fun, batched=True)
val_toeknized_ds = val.map(tokenize_fun,batched=True)

# 模型checkpoint的保存目录
output_dir = "savedmodel/zuo_aug"
log="log/"
training_args = TrainingArguments(
        save_strategy='epoch',
        num_train_epochs=20,
        per_device_train_batch_size=8, # batch_size需要根据自己GPU的显存进行设置，2080,8G显存，batch_size设置为2可以跑起来。
        logging_steps=1000,
        #fp16=True,
        # evaluation_strategy="steps",
        evaluation_strategy="epoch",
        # eval_steps=500,
        load_best_model_at_end=True,
        learning_rate=1e-5,
        # weight_decay=0.01,
        warmup_steps=100,
        output_dir=output_dir,
        save_total_limit=5,
        lr_scheduler_type='constant',
        gradient_accumulation_steps=1,
        logging_dir=log,
        dataloader_num_workers=0)

print('Training Arguments ...')
print(training_args)

trainer = Trainer(
    tokenizer=tokenizer,
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_tokenized_ds,
    eval_dataset=val_toeknized_ds
)

trainer.train()

best_model = output_dir+'/best'
# 保存最好的模型
trainer.save_model(best_model)
print("model best saved over")


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

def predict(sources, batch_size=8):
    model.eval()  # 将模型转换为评估模式
    kwargs = {"num_beams": 4,"max_new_tokens":512}
    outputs = []
    for start in (range(0, len(sources), batch_size)):
        batch = sources[start:start + batch_size]
        input_tensor = tokenizer(batch, return_tensors="pt", truncation=True, padding=True,max_length=512).input_ids.cuda()
        outputs.extend(model.generate(input_ids=input_tensor, max_length=512,**kwargs))
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)


model = T5ForConditionalGeneration.from_pretrained(best_model).cuda()
paths=[dspath+'train.json',dspath+'val.json',dspath+'test.json']
namlist=[dspath+"mt5trainpre.txt",dspath+"mt5valpre.txt",dspath+"mt5testpre.txt"]

for path,name in zip(paths,namlist):
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