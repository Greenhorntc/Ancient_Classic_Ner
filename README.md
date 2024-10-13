# Ancient_Classic_Ner
Semi-supervised ancient classic entity extraction based on knowledge distillation

项目包含以下内容：
LLM文件夹为调用各种大模型获取ner的方法
xunzi，chatgpt，spark，chatglm以及古籍翻译的api，可以自行配置对无标注文本进行处理。
从实际使用来看xunzi和chatgpt3.5的效果要优于其他两个，若使用给定文言文-现代文平行语料外的文本则可以通过文白翻译进行处理。

0：pip install -r requirements.txt
本文使用的CUDA Version: 11.7，Pyhton：3.11.0. 

1:创建两类形式的数据集，分别是：datasets类供T5类模型训练!databio供基线模型和uie训练
DatasetCreate.py 

2：sikubert+sikuroberta 使用南京农业大学团队的siku系列模型作为基座模型进行训练
https://github.com/Greenhorntc/Ancient_Classic_Ner_siku.git

3：采用Yaojie Lu等人在ACL-2022推出的uie
将数据处理为uie格式，生成式任务在模型预测速度、模型蒸馏上相对抽取式来说没有优势。https://github.com/universal-ie/UIE
更推荐使用推理和训练速度更快：https://github.com/Tongjilibo/bert4torch/tree/master/examples/sequence_labeling/uie

3：提供两种T5模型进行微调，分别是mt5和mengzi。
mT5training.py 

4：使用ZuoEvalute.py进行评估，需要将生成的结果进行回标。

