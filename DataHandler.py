"""
处理原始数据

！：原始文本
《周易正义》 -王弼等注、孔颖达疏 -阮元校刻本 9卷

  《尚书正义》 -孔安国传、孔颖达疏 -阮元校刻本 60卷

  《毛诗正义》 -郑玄笺、孔颖达疏 -阮元校刻本 71卷

  《周礼注疏》 -郑玄注、贾公彦疏 -阮元校刻本 43卷

  《仪礼注疏》 -郑玄注、贾公彦疏 -阮元校刻本 51卷

  《礼记正义》 -郑玄注、孔颖达疏 -阮元校刻本 75卷

  《春秋左传正义》 -杜预注、孔颖达疏 -阮元校刻本 61卷

  《春秋公羊传注疏》 -何休解诂、徐彦疏 -阮元校刻本 29卷

  《春秋穀梁传注疏》 -范宁注、杨士勋疏 -阮元校刻本 21卷

  《孝经注疏》 -唐玄宗注、邢昺疏 -阮元校刻本 19卷

  《尔雅注疏》 -郭璞注、邢昺疏 -阮元校刻本 16卷

  《论语注疏》 -何晏注、宋邢昺疏 -阮元校刻本 22卷

  《孟子注疏》 -赵岐注、孙奭疏 -阮元校刻本 29卷
"""

# 周易
#格式：章节标题+ 内容+[疏] 为一节
import os
import re
class Bookinfor():
    def __init__(self,file):
        self.file=file
        self.rawtxt=self.splitrawtxt()
        self.chapter=self.getchapterContentindex()

    def getchapter(self):
        rawtxt=self.rawtxt
        chapterdic={}
        #第一次遍历找到目录
        for i in range(len(rawtxt)):
            if rawtxt[i]=="目录":
                chapterdic["目录"]=i
                break
        #第二次便利找到内容
        for j in range(chapterdic["目录"]+1,len(rawtxt)):
            chapter=rawtxt[j]
            if chapter in chapterdic.keys():
                break
            if chapter not in chapterdic.keys() and chapter != "这是一行空行":
                chapterdic[rawtxt[j]]=j
            #docheck
            else:
                pass

        #获取chapterdic最后一个元素开始
        for h in range(chapterdic.get(list(chapterdic.keys())[-1])+1,len(rawtxt)):
            txt=rawtxt[h]
            if txt in chapterdic.keys():
                chapterdic[txt]=h
            else:
                pass
        chapterdic.pop('目录')
        return chapterdic

    def splitrawtxt(self):
        with open(file=self.file,encoding="ansi") as f:
            txtlist=[]
            lines=f.readlines()
            for i in range(len(lines)):
                #不得不使用空行进行内容的分割
                if lines[i].strip()=="":
                    line="这是一行空行"
                else:
                    line=lines[i].strip("\n")
                    line=line.strip("　　").strip()
                txtlist.append(line)
        return txtlist

    def getchapterContentindex(self):
        rawtxt=self.rawtxt
        chapter=self.getchapter()
        chapterlist=list(chapter.keys())
        #两个list之间获取一个tuple
        contentlist=[]
        for i in range(len(chapterlist)):
            if i==len(chapterlist)-1:
                pass
            else:
                temp=(chapter[chapterlist[i]],chapter[chapterlist[i+1]])
                contentlist.append(temp)

        contentlist.append((chapter[chapterlist[-1]],len(rawtxt)-1))
        chapterindexdic=dict(zip(chapterlist,contentlist))
        return chapterindexdic

    def getcontentbyindex(self,index):
        # print(index)
        txts=self.rawtxt[index[0]:index[1]]
        contentindex=[]
        #根据空行来选取内容
        spacelist=[]
        for i in range(len(txts)):
            if txts[i]=="这是一行空行":
                spacelist.append(i)
        #1:两行中间只要大于1那么就是content，只计算两两相互距离
        # print(spacelist)
        for i in range(len(spacelist)):
            if i==len(spacelist)-1:
                pass
            else:
                if spacelist[i+1]-spacelist[i]>1:
                    temp=(spacelist[i]+1,spacelist[i+1])
                    contentindex.append(temp)
        contentindex.append((spacelist[-1]+1,len(txts)))
        content=[]
        for index in contentindex:
            content.append(txts[index[0]:index[1]])
        return content

    def dellcontent(self,passagedata):
        bookname = ["周易正义", "尚书正义", "毛诗正义",
                    "周礼注疏", "仪礼注疏", "礼记正义",
                    "春秋左传正义", "春秋公羊传注疏", "春秋谷梁传注疏",
                    "孝经注疏", "尔雅注疏", "论语注疏", "孟子注疏"]
        keywords = bookname + ["读书中文网", "gzbysh5", "□整理", "等□疏"] + list(self.chapter.keys())
        filtered_list=[]
        for item in passagedata:
            if item and not any(keyword in subitem for subitem in item for keyword in keywords):
                filtered_list.append(item)
        return filtered_list

    def pair_text_and_comment(self,chaptername):
        lst=self.getcontentbyindex(self.chapter[chaptername])
        lst=self.dellcontent(lst)
        pairs = []
        for item in lst:
            text = ""
            comment = ""
            #定位[疏]所在的位置，以上全为文本，[疏]之下
            #1先看有没有[疏]
            for i in range(len(item)):
                if "[疏]" in item[i]:
                    mark=i
                else:
                    mark=0
            if mark==0:
                for subitem in item:
                    text = text+subitem
            else:
                textlist=item[:mark]
                commentlst=item[mark:]
                text= "".join(textlist)
                # print(text)
                # print("txt")
                comment="".join(commentlst)
                # print(comment)
                # print("zhushi")
            pairs.append((text, comment))

        return pairs

class ZuoZhuan():
    def __init__(self,file):
        self.file=file
        self.rawtxt=self.readfile()

    def readfile(self):
        with open(file=self.file,encoding="utf-8")as f:
            lines=f.readlines()[183:72038]
        txtlist=[]
        for i in range(len(lines)):
            # 不得不使用空行进行内容的分割
            if lines[i].strip() == "":
                pass
            else:
                line = lines[i].strip("\n")
                line = line.strip("　　").strip()
                txtlist.append(line)
        return txtlist

    def get_ortxt(self,orindex,txt):
        a_content=[]
        end=0
        for i in range(orindex + 1, len(txt)):
            #找到结束的这行只要是} 无论是注释还是译文
            if txt[i].endswith("】"):
                end=i
                break
            a_content.append(txt[i])
        # print(a_content)
        expanlinidex=0
        #:会出现中间没有注释的情况直接跳到译文
        if txt[end]=="【译文】":
            b_expaination = txt[end + 1:end + 1 + len(a_content)]
        else:
            for k in range(end+1,len(txt)):
                if txt[k].endswith("【译文】"):
                    expanlinidex=k
                    break
            b_expaination=txt[expanlinidex+1:expanlinidex+1+len(a_content)]
        return a_content,b_expaination

    def get_expan(self,index,txt):
        a_content = []
        end = 0
        #为什么会不一样呢，因为这里取到的已经是文本内容了
        for i in range(index, len(txt)):
            # 找到结束的这行只要是} 无论是注释还是译文
            if txt[i].endswith("】"):
                end=i
                break
            a_content.append(txt[i])
        # print(a_content)
        expanlinidex = 0
        #:会出现中间没有注释的情况直接跳到译文
        if txt[end] == "【译文】":
            b_expaination = txt[end + 1:end + 1 + len(a_content)]
        else:
            for k in range(end + 1, len(txt)):
                if txt[k].endswith("【译文】"):
                    expanlinidex = k
                    break
            b_expaination = txt[expanlinidex + 1:expanlinidex + 1 + len(a_content)]
        # print(len(a_content))
        # print(a_content)
        # print(b_expaination)
        # print("-----")
        return a_content,b_expaination

    def remove_marks(self,text):
        text = re.sub(r'\[\d+\]', '', text)  # 去掉 [1] 这样的标记
        text = re.sub(r'\u3000', '', text)  # 去掉 \u3000 这样的标记
        text = re.sub(r'\d+\.\d+', '', text)
        return text

    def clean_data(self,datalist):
        for data in datalist:
            data[0]=self.remove_marks(data[0])
            data[1]=self.remove_marks(data[1])
            print(data)
        return datalist


    def get_content_pair(self):
        jin=[]
        zhuan=[]
        restdata=[]
        ortxttemp = []
        ortxttemp2 = []
        txt=self.rawtxt
        # 找到标签A所在的位置
        for i in range(len(txt)):
            if txt[i]=="【传】":
                ortxttemp.append(i)
            if txt[i]=="【经】":
                ortxttemp2.append(i)
            else:
                pass
        # 提取标签A之后直到下一个标签之前的内容
        for orindex in ortxttemp:
            content,expan=self.get_ortxt(orindex,txt)
            for con,ex in zip(content,expan):
                jin.append([con,ex])
        for index in ortxttemp2:
            content, expan = self.get_ortxt(index, txt)
            for con, ex in zip(content, expan):
                zhuan.append([con, ex])
        # 还有一种开头既没有【传】，也没【经】,去掉上面两个有的就是剩下的
        pattern = r"^\d.*"
        digit_start_sentences = [(i, sentence) for i, sentence in enumerate(txt) if re.match(pattern, sentence)]

        ortxttemp3=[]
        lst=[x[0] for x in (jin+zhuan)]
        for index, sentence in digit_start_sentences:
            #1:看看在不在dataall里面
            if sentence in lst:
                pass
            else:
                ortxttemp3.append(index)
        for orindex in ortxttemp3:
            content,expan=self.get_expan(orindex,txt)
            for con, ex in zip(content, expan):
                restdata.append([con, ex])

        # for data in dataall:
        dataall=self.clean_data(jin+zhuan+restdata)
        return dataall

# datafile="data/Zuo/四书五经.txt"
# zuozhuan=ZuoZhuan(datafile)
# zuodatalist=zuozhuan.get_content_pair()
# print(zuodatalist)


