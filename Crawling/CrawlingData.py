# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 11:31:58 2018

@author: ShangFR
"""
import requests
import pandas as pd
import jieba
import jieba.analyse
import codecs
import re

#导入自定义词典
jieba.load_userdict("data\\stock_dict.txt")
#载入停用词
jieba.analyse.set_stop_words('data\\stop_words.txt')
stopwords = [line.strip() for line in codecs.open('data\\stop_words.txt', 'r', 'utf-8').readlines()] 
jieba.add_word('传闻求证')

def valuemap(words_value,xmax,xmin):
    '''
    valuemap    
    Description:
        ymaxymax 要映射的目标区间最大值 
        yminymin 要映射的目标区间最小值 
        xmaxxmax 目前数据最大值 
        xminxmin 目前数据最小值 
        xx 假设目前数据中的任一值 
        yy 归一化映射后的值

    :param tscode: words_value.
    '''
    ymax = 30
    ymin = 10   
    y = ymin + (ymax-ymin)/(xmax-xmin)*(words_value-xmin)
    return y


def keyword(news_df):
    '''
    Extraction of keywords
    
    Description:
        提取title的关键词

    :param tscode: stock code.
    '''
    print("正在进行关键词提取：")
    news_df = news_df.dropna(axis=0, how='any',inplace=False)
    news_list = list(news_df['title'])
    
    segments = []
    splitedStr = ''
    for title in news_list:
        content = re.sub("[A-Za-z0-9\[\`\~\!\@\#\$\^\&\*\(\)\=\__\___\____\©\·\■\□\✦\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\！\@\#\\\&\+\-\*\%]", "", title)
        content = content.replace(' ','')
        #TextRank 关键词抽取，只获取固定词性
        #words = jieba.analyse.textrank(content, topK=5,withWeight=False,allowPOS=('ns', 'n', 'vn', 'v'))
        words = jieba.cut(content, cut_all=False)
        
        for word in words:
            if word not in stopwords:
                # 记录全局分词
                segments.append({'word':word, 'count':1})
                splitedStr += word + ' '
    dfSg = pd.DataFrame(segments)
    # 词频统计
    dfWord = dfSg.groupby('word')['count'].sum()
    name = list(dfWord.index)#词
    value = dfWord.values#词的频率
    xmax = max(value)
    xmin = min(value)
    value2 = list(map(lambda x:valuemap(x,xmax,xmin), value))
    wordFreq = pd.DataFrame({'name': name, 'value': value2})
    return wordFreq
    

send_headers={
        "Accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Connection":"keep-alive",
        "Cookie":"_ga=GA1.2.1572531392.1543464819; device_id=49e155ac9f24fc445a86af50f067777f; s=ec127e6due; bid=c9496d241ef94c901020f91e8fb6f0f8_jp9fwg8b; __utmz=1.1545362273.25.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _gid=GA1.2.1743612026.1546393698; xq_token_expire=Sun%20Jan%2027%202019%2009%3A55%3A45%20GMT%2B0800%20(CST); aliyungf_tc=AQAAAOwF6lbEnQkADaqEOsMhcpi0ZNak; xq_a_token=2cc0db8e6c9557881ce4ae8b65d9f3eae93590b1; xq_a_token.sig=qv3nJrKcwm71Wmn6VnmIziG87qM; xq_r_token=ab2c0900d65938325f88ac73946415218dcaa514; xq_r_token.sig=HBp5A4Ecbuxvczk4cLwQQ8CblLs; Hm_lvt_1db88642e346389874251b5a1eded6e3=1546393696,1546402310,1546484134,1546491991; u=481546491991172; _gat_gtag_UA_16079156_4=1; __utma=1.1572531392.1543464819.1546484137.1546496107.37; __utmc=1; __utmt=1; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1546496119; __utmb=1.3.10.1546496107",
        "Host":"xueqiu.com",
        "Referer":"https://xueqiu.com/S/SZ002230",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "X-Requested-With":"XMLHttpRequest"
        } #伪装浏览器

def crawling(scode,count):
    '''
    Data Crawling

    Description:
        雪球网个股新闻页面舆情数据爬取，包含新闻标题、发布时间、转发数、评论数、点赞数和新闻概要。

    :param scode: stock code.
    :param count: count.
    '''
    news_df = pd.DataFrame(columns=["id","title","created_at","like_count","reply_count","retweet_count"])
    page = 1
    r = requests.get('https://xueqiu.com/statuses/stock_timeline.json?symbol_id='+scode+'&count=20&source=%E8%87%AA%E9%80%89%E8%82%A1%E6%96%B0%E9%97%BB&page='+str(page), headers=send_headers)
    #r.encoding = r.apparent_encoding   
    #content = r.text
    #news = json.loads(content)
    news = r.json()
    if r.status_code != 200:
        print(news["error_description"])
    df = pd.DataFrame(news["list"], columns=["id","title","created_at","like_count","reply_count","retweet_count"])
    news_df=news_df.append(df)
    print("第%s次请求，成功" % page)
    return news_df










