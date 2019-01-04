# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 09:57:35 2019

@author: ShangFR
"""

import requests
import pandas as pd
import codecs
import re

send_headers={
        "Accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Connection":"keep-alive",
        "Cookie":"_ga=GA1.2.1572531392.1543464819; device_id=49e155ac9f24fc445a86af50f067777f; s=ec127e6due; bid=c9496d241ef94c901020f91e8fb6f0f8_jp9fwg8b; xq_a_token.sig=o6mn8Yky2SBZ0vIINuna-UTrXEQ; xq_r_token.sig=dFyrAc_PRVOcmE8X07-ieu0FOkM; Hm_lvt_1db88642e346389874251b5a1eded6e3=1545874962,1545890725,1545961448,1546393696; _gid=GA1.2.1743612026.1546393698; xq_a_token=6fbeaf67d804f5ee727ddb78d0079d8a64a6c79a; xqat=6fbeaf67d804f5ee727ddb78d0079d8a64a6c79a; xq_r_token=272e550c571994bf6c9d94156baa1b88712a713a; xq_token_expire=Sun%20Jan%2027%202019%2009%3A55%3A45%20GMT%2B0800%20(CST); xq_is_login=1; u=2958546835; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1546395882; _gat_gtag_UA_16079156_4=1",
        "Host":"stock.xueqiu.com",
        "Origin":"https://xueqiu.com",
        "Referer":"https://xueqiu.com/S/SH000300",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "X-Requested-With":"XMLHttpRequest"
        } #伪装浏览器


r = requests.get('https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SH000300&begin=1546395906142&period=day&type=before&count=-142&indicator=kline,ma', headers=send_headers)
#r.encoding = r.apparent_encoding   
#content = r.text
#news = json.loads(content)
news = r.json()
df = news["data"]

df = pd.DataFrame(df["item"], columns=df["column"])

df['date'] = pd.to_datetime(df['timestamp']/1000,  unit='s') #将数据类型转换为日期类型


df.to_csv("data/hs300.csv")







