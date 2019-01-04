#coding:utf-8

from flask import Flask, request, render_template, url_for,Markup
import json
import pandas as pd
# Crawling, Tidy & Transformation Data
from Crawling.CrawlingData import crawling,keyword
from Crawling.Jukuan import jdstock
# 生成Flask实例
app = Flask(__name__)
stocks = pd.read_csv ("data/stocks.csv" , encoding = "utf-8", dtype={'symbol': str})
deal = pd.read_csv ("data/deal.csv" , encoding = "utf-8", dtype={'code': str}) 
deal['dayhold']=100*(1-deal['cash']/deal['total'])
deal = deal.round({'dayhold': 1})

fundDF = pd.read_csv ("data/db300.csv" , encoding = "utf-8")

fundPerformance = fundDF[["db","hs300"]].cumsum()
fundPerformance['date'] = fundDF['date']

fundDF['date1'] = pd.to_datetime(fundDF['date'],format='%Y%m%d') #将数据类型转换为日期类型
fundProfit = fundDF.set_index('date1') # 将date设置为index
fundProfit = fundProfit[["db","hs300"]].resample('W').sum()
fundProfit = fundProfit.round({'db': 2,'hs300': 2})

@app.route('/')
def index():
    deals = deal.to_dict('records')
    fundlist0 = fundPerformance.to_dict('list')
    fundlist1 = fundProfit.to_dict('list')
    return render_template('home.html',stocks=deals, fundline = fundlist0, fundbar = fundlist1)

# 跳转详情
@app.route('/details/<code_id>')  #将id带到控制器
def detailview(code_id):
    stockinfo = stocks[stocks['symbol']==code_id]
    scode = stockinfo.ts_code.tolist()[0]
    news_df = crawling((scode[7:9]+scode[0:6]),1)
    wordFreq = keyword(news_df)
    wordFreq = wordFreq.to_json(orient='records')
    dailyk = jdstock(code_id)
    return render_template('details.html',info=stockinfo.to_dict('records')[0], wf = Markup(wordFreq),k=Markup(dailyk["data"]))

    
if __name__ == '__main__':
    # 运行项目
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
