# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import requests
import random
import json
import time
from hashlib import md5
from DataTools import readNer,get_ortxt,write_json
# Set your own appid/appkey.
appid = ''
appkey = ''

# For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
from_lang = 'wyw'
to_lang =  'zh'

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path
# query = '玄龄、如晦不以旧进，特其才可与治天下者'
# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()
def sengpost(query):
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)
    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    # Send request
    time.sleep(0.5)
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    # Show response
    print(json.dumps(result, indent=4, ensure_ascii=False))
    sentence=result["trans_result"][0]["dst"]
    return sentence

def get_translate(filename):
    result=[]
    datalist=readNer(filename)
    for data in datalist:
        q,a=get_ortxt(data)
        translate=sengpost(q)
        data["tranlate"]=translate
        result.append(data)
    return result

def getfiledone(filename,savename):
    data = get_translate(filename)
    write_json(data, savename)
    print("====")


