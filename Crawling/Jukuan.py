# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 09:57:35 2019

@author: ShangFR
"""


import jqdatasdk as jd
jd.auth("15501151056","151056") 
import pandas as pd
import numpy as np
import datetime

#将所有股票列表转换成数组
stocks = jd.get_all_securities('stock')
codes = list(stocks.index)

def jdstock(code):
    '''
    valuemap    
    Description:
        yy 归一化映射后的值

    :param tscode: words_value.
    '''

    code = {'code': [code+'.XSHE',code+'.XSHG']}
    df = pd.DataFrame(data=code)
    scode = df[df["code"].isin(codes)]
    scode = scode.reset_index(drop=True)
    df = jd.get_price(scode["code"][0], start_date='2018-01-01',end_date=datetime.date.today(), frequency='daily')
    df['money'] = np.where(df["open"]>df["close"], 1, -1)
    df['date'] = df.index.strftime("%Y-%m-%d")
    order = [ 'date','open', 'high', 'low','close',  'volume', 'money']
    df = df[order]
    sdf = df.to_dict('split')
    return sdf


