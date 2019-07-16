# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:19:44 2019

@author: ShangFR
"""

import pandas as pd
from WindPy import *
from sqlalchemy import create_engine
import datetime,time
import os
root = os.getcwd()               #获得当前路径 /home/dir1
print(root)
pd.set_option('mode.chained_assignment',None)

# %% cell 1
class WindStock:
 
    def getCurrentTime(self):
        # 获取当前时间
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime())

    def getAStockCodesWind(self,end_date=time.strftime('%Y%m%d',time.localtime())):
        '''
        如设定日期参数，则获取参数指定日期所有A股代码，不指定日期参数则默认为当前日期
        :return: 指定日期所有A股代码，不指定日期默认为最新日期
        '''
        w.start()
        print(self.getCurrentTime(),": get A Stock Codes from Wind Starting:")
        stockCodes=w.wset("sectorconstituent","date="+end_date+";sectorid=a001010100000000;field=wind_code")
        return stockCodes.Data[0]

    def getPrediction(self,symbols,end_date=time.strftime('%Y%m%d',time.localtime())):
        print(self.getCurrentTime(),": get Prediction data from Wind Starting:")
        data00 = w.wss(symbols, "yoynetprofit","rptDate=20181231")
        data01 = w.wss(symbols, "est_yoynetprofit","year=2019;tradeDate="+end_date+"")
        data02 = w.wss(symbols, "est_yoynetprofit","year=2020;tradeDate="+end_date+"")
        data03 = w.wss(symbols, "est_yoynetprofit","year=2021;tradeDate="+end_date+"")
        
        df00 = pd.DataFrame({'t1': data00.Data[0],'p1': data01.Data[0], 'p2': data02.Data[0],'p3': data03.Data[0]},index=data00.Codes).fillna(method="ffill", axis=1)
        df00.fillna(0, inplace=True)
        df00['p'] = (df00.p1+df00.p2+df00.p3)/3
        df00['A'] = (df00.t1-df00.p)/abs(df00.t1)
    
        df01 = df00[['A']]
        df01.insert(1,'score0',1) 
        df01.score0[df01['A']> 0.7]= 1
        df01.score0[(df01['A']> 0.5) & (df01['A']<= 0.7)]= 2
        df01.score0[(df01['A']> 0.3) & (df01['A']<= 0.5)]= 3
        df01.score0[(df01['A']> 0.1) & (df01['A']<= 0.3)]= 4
        df01.score0[(df01['A']> 0) & (df01['A']<= 0.1)]= 5
        
        return df01.score0


    def getValuation(self,symbols,end_date=time.strftime('%Y%m%d',time.localtime())):
        print(self.getCurrentTime(),": get Valuation data from Wind Starting:")
        data00 = w.wss(symbols, "pe_ttm,pb_lf,yoy_tr,yoynetprofit,industry_sw","tradeDate=20190630;rptDate="+end_date+";industryType=2")
        
        df00 = pd.DataFrame({'pe': data00.Data[0],'pb': data00.Data[1],'yoy_tr':data00.Data[2],"yoynetprofit":data00.Data[3],'industry':data00.Data[4]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(5,'label','成熟性行业') 
        df00.label[df00['yoy_tr']>= 30]= '高增长行业'
        df00.label[(df00['yoy_tr']>= 15) & (df00['yoy_tr']< 30)]= '中等成长行业'
        df00.insert(6,'score0',1) 
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.pe.count() > 10:
                try:
                    bins = group.pe.quantile([0, .2, .4, .6, .8, 1])
                    labels = [5, 4, 3, 2, 1]
                    df00.loc[df00['industry'] == name,"score0"] = pd.cut(group.pe, bins, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass
    
        df01 = df00[['pe',"yoynetprofit","label"]]
        df01.insert(3,'PEG',df01['pe']/df01['yoynetprofit']) 
        df01.insert(4,'score1',1) 
        df01.score1[(df01['label'] == '成熟性行业') & (df01['pe']<= 0)]= 0
        df01.score1[(df01['label'] == '成熟性行业') & (df01['pe']> 0)& (df01['pe']<= 10)]= 5
        df01.score1[(df01['label'] == '成熟性行业') & (df01['pe']> 10) & (df01['pe']<= 15)]= 4
        df01.score1[(df01['label'] == '成熟性行业') & (df01['pe']> 15) & (df01['pe']<= 20)]= 3
        df01.score1[(df01['label'] == '成熟性行业') & (df01['pe']> 20) & (df01['pe']<= 30)]= 2
    
        df01.score1[(df01['label'] == '中等成长行业') & (df01['PEG']<= 0)]= 0
        df01.score1[(df01['label'] == '中等成长行业') & (df01['PEG']> 0)& (df01['PEG']<= 1)]= 5
        df01.score1[(df01['label'] == '中等成长行业') & (df01['PEG']> 1) & (df01['PEG']<= 1.5)]= 4
        df01.score1[(df01['label'] == '中等成长行业') & (df01['PEG']> 1.5) & (df01['PEG']<= 2)]= 3
        df01.score1[(df01['label'] == '中等成长行业') & (df01['PEG']> 2) & (df01['PEG']<= 3)]= 2
    
        df01.score1[(df01['label'] == '高增长行业') & (df01['PEG']<= 0)]= 0
        df01.score1[(df01['label'] == '高增长行业') & (df01['PEG']> 0)& (df01['PEG']<= 1)]= 5
        df01.score1[(df01['label'] == '高增长行业') & (df01['PEG']> 1) & (df01['PEG']<= 1.5)]= 4
        df01.score1[(df01['label'] == '高增长行业') & (df01['PEG']> 1.5) & (df01['PEG']<= 2)]= 3
    
        df00.insert(7,'score2',1) 
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.pb.count() > 10:
                try:
                    bins = group.pb.quantile([0, .2, .4, .6, .8, 1])
                    labels = [5, 4, 3, 2, 1]
                    df00.loc[df00['industry'] == name,"score0"] = pd.cut(group.pb, bins, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass
        
        
        df02 = df00[['pb',"yoynetprofit","label"]]
        df02.insert(3,'score3',1) 
        df02.score3[(df02['label'] == '成熟性行业') & (df02['pb']<= 0)]= 0
        df02.score3[(df02['label'] == '成熟性行业') & (df02['pb']> 0)& (df02['pb']<= 1.5)]= 5
        df02.score3[(df02['label'] == '成熟性行业') & (df02['pb']> 1.5) & (df02['pb']<= 2)]= 4
        df02.score3[(df02['label'] == '成熟性行业') & (df02['pb']> 2) & (df02['pb']<= 3)]= 3
        df02.score3[(df02['label'] == '成熟性行业') & (df02['pb']> 3) & (df02['pb']<= 4)]= 2
    
        df02.score3[(df02['label'] != '成熟性行业') & (df02['pb']<= 0)]= 0
        df02.score3[(df02['label'] != '成熟性行业') & (df02['pb']> 0)& (df02['pb']<= 2)]= 5
        df02.score3[(df02['label'] != '成熟性行业') & (df02['pb']> 2) & (df02['pb']<= 3)]= 4
        df02.score3[(df02['label'] != '成熟性行业') & (df02['pb']> 3) & (df02['pb']<= 4)]= 3
        df02.score3[(df02['label'] != '成熟性行业') & (df02['pb']> 4) & (df02['pb']<= 6)]= 2
    
        df00["score"] = 0.5*(0.5*df00.score0+0.5*df01.score1)+0.5*(0.5*df00.score2+0.5*df02.score3)
        
        return df00.score

    def getGrow(self,symbols):
        print(self.getCurrentTime(),": get Grow up data from Wind Starting")
        data00 = w.wss(symbols,"yoy_tr,yoynetprofit,yoynetprofit_deducted,industry_sw","rptDate=20181231;industryType=2")
        
        df00 = pd.DataFrame({'yoy_tr': data00.Data[0],'yoy': data00.Data[1],'yoy_de':data00.Data[2],'industry':data00.Data[3]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(4,'score0',1) 
        df00.insert(5,'score1',1) 
        df00.insert(6,'score2',1) 
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.yoy_tr.count() > 10:
                try:
                    bins0 = group.yoy_tr.quantile([0, .2, .4, .6, .8, 1])
                    bins1 = group.yoy.quantile([0, .2, .4, .6, .8, 1])
                    bins2 = group.yoy_de.quantile([0, .2, .4, .6, .8, 1])
                    labels = [5, 4, 3, 2, 1]
                    df00.loc[df00['industry'] == name,"score0"] = pd.cut(group.yoy_tr, bins0, labels = labels, include_lowest=True)
                    df00.loc[df00['industry'] == name,"score1"] = pd.cut(group.yoy, bins1, labels = labels, include_lowest=True)
                    df00.loc[df00['industry'] == name,"score2"] = pd.cut(group.yoy_de, bins2, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass    
        print(self.getCurrentTime(),": 趋势打分:")
        data01 = w.wss(symbols,"yoy_tr,yoynetprofit,yoynetprofit_deducted","rptDate=20171231")
        data02 = w.wss(symbols,"yoy_tr,yoynetprofit,yoynetprofit_deducted","rptDate=20161231")
        data03 = w.wss(symbols,"yoy_tr,yoynetprofit,yoynetprofit_deducted","rptDate=20151231")   
        df01 = pd.DataFrame({'yoy_tr18': data00.Data[0],'yoy_tr17': data01.Data[0],'yoy_tr16': data02.Data[0],'yoy_tr15': data03.Data[0]},index=data00.Codes)
        df02 = pd.DataFrame({'yoy18': data00.Data[1],'yoy17': data01.Data[1],'yoy16': data02.Data[1],'yoy15': data03.Data[1]},index=data00.Codes)
        df03 = pd.DataFrame({'yoy_de18': data00.Data[2],'yoy_de17': data01.Data[2],'yoy_de16': data02.Data[2],'yoy_de15': data03.Data[2]},index=data00.Codes)
        
        df01["x"] = df01['yoy_tr18']>df01['yoy_tr17']
        df01["y"] = df01['yoy_tr17']>df01['yoy_tr16']
        df01["z"] = df01['yoy_tr16']>df01['yoy_tr15']
        df02["x"] = df02['yoy18']>df02['yoy17']
        df02["y"] = df02['yoy17']>df02['yoy16']
        df02["z"] = df02['yoy16']>df02['yoy15']
        df03["x"] = df03['yoy_de18']>df03['yoy_de17']
        df03["y"] = df03['yoy_de17']>df03['yoy_de16']
        df03["z"] = df03['yoy_de16']>df03['yoy_de15']
        
        df00["score00"] = df01.loc[:,["x","y","z"]].apply(lambda x: x.sum(), axis=1).replace([0, 1, 2, 3], [2, 3, 4.5, 5])
        df00["score01"] = df02.loc[:,["x","y","z"]].apply(lambda x: x.sum(), axis=1).replace([0, 1, 2, 3], [2, 3, 4.5, 5])
        df00["score02"] = df03.loc[:,["x","y","z"]].apply(lambda x: x.sum(), axis=1).replace([0, 1, 2, 3], [2, 3, 4.5, 5])
        
        df00["score"] = 0.3*(0.7*df00["score0"]+0.3*df00["score00"])+0.2*(0.7*df00["score1"]+0.3*df00["score01"])+0.35*(0.7*df00["score2"]+0.3*df00["score02"])
        
        return df00.score
  
    def getDividend(self,symbols,end_date=time.strftime('%Y%m%d',time.localtime())):
        print(self.getCurrentTime(),": get Dividend data from Wind Starting:")
        data00 = w.wss(symbols,"dividendyield2,industry_sw","tradeDate="+end_date+";industryType=2")
        df00 = pd.DataFrame({'dividend': data00.Data[0],'industry': data00.Data[1]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(2,'score0',1)
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.dividend.count() > 10:
                try:
                    bins = group.dividend.quantile([0, .5, .8, 1])
                    labels = [1, 3, 5]
                    df00.loc[df00['industry'] == name,"score0"] = pd.cut(group.dividend, bins, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass 
        return df00.score0
    
    def getRoe(self,symbols):
        print(self.getCurrentTime(),": get Roe data from Wind Starting")
        data00 = w.wss(symbols,"roe_ttm2,industry_sw","rptDate=20181231;industryType=2")
        df00 = pd.DataFrame({'roe': data00.Data[0],'industry': data00.Data[1]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(2,'score0',1) 
        df00.insert(3,'score1',1) 
        df00.insert(4,'score2',1)         
        bins = [df00.roe.min(), 6, 10, 15, 20, df00.roe.max()]
        labels = [1, 2, 3, 4, 5]
        df00.loc[:,"score0"] = pd.cut(df00.roe, bins, labels = labels, include_lowest=True)
        df00.loc[:,"score0"] = df00['score0'].astype('int') 
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.roe.count() > 10:
                try:
                    bins = group.roe.quantile([0, .2, .4, .6, .8, 1])
                    labels = [1, 2, 3, 4, 5]
                    df00.loc[df00['industry'] == name,"score1"] = pd.cut(group.roe, bins, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass 
        print(self.getCurrentTime(),": 趋势打分:")
        data01 = w.wss(symbols,"roe_ttm2","rptDate=20171231")
        data02 = w.wss(symbols,"roe_ttm2","rptDate=20161231")
        data03 = w.wss(symbols,"roe_ttm2","rptDate=20151231") 
        df01 = pd.DataFrame({'roe_ttm218': data00.Data[0],'roe_ttm217': data01.Data[0],'roe_ttm216': data02.Data[0],'roe_ttm215': data03.Data[0]},index=data00.Codes)        
        df01["x"] = df01['roe_ttm218']>df01['roe_ttm217']
        df01["y"] = df01['roe_ttm217']>df01['roe_ttm216']
        df01["z"] = df01['roe_ttm216']>df01['roe_ttm215']
        df00["score2"] = df01.loc[:,["x","y","z"]].apply(lambda x: x.sum(), axis=1).replace([0, 1, 2, 3], [2, 3, 4.5, 5])
        df00["score"] = 0.7*df00["score0"]+0.15*df00["score1"]+0.15*df00["score2"]
        
        return df00.score
    
    def getNetprofit(self,symbols):
        print(self.getCurrentTime(),": get netprofit data from Wind Starting")
        data00 = w.wss(symbols,"netprofitmargin,industry_sw","rptDate=20181231;industryType=2")
        df00 = pd.DataFrame({'netprofit': data00.Data[0],'industry': data00.Data[1]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(2,'score0',1) 
        df00.insert(3,'score1',1) 
        df00.insert(4,'score2',1)         
        bins = [df00.netprofit.min(), 3, 5, 10, 15, df00.netprofit.max()]
        labels = [1, 2, 3, 4, 5]
        df00.loc[:,"score0"] = pd.cut(df00.netprofit, bins, labels = labels, include_lowest=True)
        df00.loc[:,"score0"] = df00['score0'].astype('int') 
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.netprofit.count() > 10:
                try:
                    bins = group.netprofit.quantile([0, .2, .4, .6, .8, 1])
                    labels = [1, 2, 3, 4, 5]
                    df00.loc[df00['industry'] == name,"score1"] = pd.cut(group.netprofit, bins, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass 
        print(self.getCurrentTime(),": 趋势打分:")
        data01 = w.wss(symbols,"netprofitmargin","rptDate=20171231")
        data02 = w.wss(symbols,"netprofitmargin","rptDate=20161231")
        data03 = w.wss(symbols,"netprofitmargin","rptDate=20151231") 
        df01 = pd.DataFrame({'netprofitmargin18': data00.Data[0],'netprofitmargin17': data01.Data[0],'netprofitmargin16': data02.Data[0],'netprofitmargin15': data03.Data[0]},index=data00.Codes)        
        df01["x"] = df01['netprofitmargin18']>df01['netprofitmargin17']
        df01["y"] = df01['netprofitmargin17']>df01['netprofitmargin16']
        df01["z"] = df01['netprofitmargin16']>df01['netprofitmargin15']
        df00["score2"] = df01.loc[:,["x","y","z"]].apply(lambda x: x.sum(), axis=1).replace([0, 1, 2, 3], [2, 3, 4.5, 5])
        df00["score"] = 0.6*df00["score0"]+0.2*df00["score1"]+0.2*df00["score2"]
        
        return df00.score
    
    def getGrossprofit(self,symbols):
        print(self.getCurrentTime(),": get grossprofit data from Wind Starting")
        data00 = w.wss(symbols,"grossprofitmargin,industry_sw","rptDate=20181231;industryType=2")
        df00 = pd.DataFrame({'grossprofit': data00.Data[0],'industry': data00.Data[1]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(2,'score0',1) 
        df00.insert(3,'score1',1) 
        df00.insert(4,'score2',1)         
        bins = [df00.grossprofit.min(), 10, 20, 40, 60, df00.grossprofit.max()]
        labels = [1, 2, 3, 4, 5]
        df00.loc[:,"score0"] = pd.cut(df00.grossprofit, bins, labels = labels, include_lowest=True)
        df00.loc[:,"score0"] = df00['score0'].astype('int') 
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.grossprofit.count() > 10:
                try:
                    bins = group.grossprofit.quantile([0, .2, .4, .6, .8, 1])
                    labels = [1, 2, 3, 4, 5]
                    df00.loc[df00['industry'] == name,"score1"] = pd.cut(group.grossprofit, bins, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass 
        print(self.getCurrentTime(),": 趋势打分:")
        data01 = w.wss(symbols,"grossprofitmargin","rptDate=20171231")
        data02 = w.wss(symbols,"grossprofitmargin","rptDate=20161231")
        data03 = w.wss(symbols,"grossprofitmargin","rptDate=20151231") 
        df01 = pd.DataFrame({'grossprofitmargin18': data00.Data[0],'grossprofitmargin17': data01.Data[0],'grossprofitmargin16': data02.Data[0],'grossprofitmargin15': data03.Data[0]},index=data00.Codes)        
        df01["x"] = df01['grossprofitmargin18']>df01['grossprofitmargin17']
        df01["y"] = df01['grossprofitmargin17']>df01['grossprofitmargin16']
        df01["z"] = df01['grossprofitmargin16']>df01['grossprofitmargin15']
        df00["score2"] = df01.loc[:,["x","y","z"]].apply(lambda x: x.sum(), axis=1).replace([0, 1, 2, 3], [2, 3, 4.5, 5])
        df00["score"] = 0.6*df00["score0"]+0.2*df00["score1"]+0.2*df00["score2"]
        
        return df00.score

    def getDeductedprofit(self,symbols):
        print(self.getCurrentTime(),": get deductedprofit data from Wind Starting")
        data00 = w.wss(symbols,"deductedprofittoprofit,industry_sw","rptDate=20181231;industryType=2")
        df00 = pd.DataFrame({'deductedprofit': data00.Data[0],'industry': data00.Data[1]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(2,'score0',1)         
        bins = [df00.deductedprofit.min(),60, 70, 80, 85, 90, df00.deductedprofit.max()]
        labels = [0,1, 2, 3, 4, 5]
        df00.loc[:,"score0"] = pd.cut(df00.deductedprofit, bins, labels = labels, include_lowest=True)
        df00.loc[:,"score0"] = df00['score0'].astype('int') 
        return df00.score0
        
    def getCashin(self,symbols):
        print(self.getCurrentTime(),": get cashin data from Wind Starting")
        data00 = w.wss(symbols,"salescashintoor,industry_sw","rptDate=20181231;industryType=2")
        df00 = pd.DataFrame({'cashin': data00.Data[0],'industry': data00.Data[1]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(2,'score0',1) 
        df00.insert(3,'score1',1) 
        df00.insert(4,'score2',1)         
        bins = [df00.cashin.min(), 30, 50, 60, 80, 100, df00.cashin.max()]
        labels = [0, 1, 2, 3, 4, 5]
        df00.loc[:,"score0"] = pd.cut(df00.cashin, bins, labels = labels, include_lowest=True)
        df00.loc[:,"score0"] = df00['score0'].astype('int') 
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.cashin.count() > 10:
                try:
                    bins = group.cashin.quantile([0, .2, .4, .6, .8, 1])
                    labels = [1, 2, 3, 4, 5]
                    df00.loc[df00['industry'] == name,"score1"] = pd.cut(group.cashin, bins, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass 
        print(self.getCurrentTime(),": 趋势打分:")
        data01 = w.wss(symbols,"salescashintoor","rptDate=20171231")
        data02 = w.wss(symbols,"salescashintoor","rptDate=20161231")
        data03 = w.wss(symbols,"salescashintoor","rptDate=20151231") 
        df01 = pd.DataFrame({'salescashintoor18': data00.Data[0],'salescashintoor17': data01.Data[0],'salescashintoor16': data02.Data[0],'salescashintoor15': data03.Data[0]},index=data00.Codes)        
        df01["x"] = df01['salescashintoor18']>df01['salescashintoor17']
        df01["y"] = df01['salescashintoor17']>df01['salescashintoor16']
        df01["z"] = df01['salescashintoor16']>df01['salescashintoor15']
        df00["score2"] = df01.loc[:,["x","y","z"]].apply(lambda x: x.sum(), axis=1).replace([0, 1, 2, 3], [2, 3, 4.5, 5])
        df00["score"] = 0.6*df00["score0"]+0.2*df00["score1"]+0.2*df00["score2"]
        
        return df00.score

    def getIncome(self,symbols):
        print(self.getCurrentTime(),": get income data from Wind Starting")
        data00 = w.wss(symbols,"ocftooperateincome,industry_sw","rptDate=20181231;industryType=2")
        df00 = pd.DataFrame({'income': data00.Data[0],'industry': data00.Data[1]},index=data00.Codes)
        df00.fillna(0, inplace=True)
        df00.insert(2,'score0',1) 
        df00.insert(3,'score1',1) 
        df00.insert(4,'score2',1)         
        bins = [df00.income.min(), 6, 10, 15, 20, df00.income.max()]
        labels = [1, 2, 3, 4, 5]
        df00.loc[:,"score0"] = pd.cut(df00.income, bins, labels = labels, include_lowest=True)
        df00.loc[:,"score0"] = df00['score0'].astype('int') 
        for name, group in df00.groupby('industry'):
            #print(name)
            if group.income.count() > 10:
                try:
                    bins = group.income.quantile([0, .2, .4, .6, .8, 1])
                    labels = [1, 2, 3, 4, 5]
                    df00.loc[df00['industry'] == name,"score1"] = pd.cut(group.income, bins, labels = labels, include_lowest=True)
                except Exception as e:
                    print("Exception :%s" % (e) )
                    continue
            else:
                pass 
        print(self.getCurrentTime(),": 趋势打分:")
        data01 = w.wss(symbols,"ocftooperateincome","rptDate=20171231")
        data02 = w.wss(symbols,"ocftooperateincome","rptDate=20161231")
        data03 = w.wss(symbols,"ocftooperateincome","rptDate=20151231") 
        df01 = pd.DataFrame({'ocftooperateincome18': data00.Data[0],'ocftooperateincome17': data01.Data[0],'ocftooperateincome16': data02.Data[0],'ocftooperateincome15': data03.Data[0]},index=data00.Codes)        
        df01["x"] = df01['ocftooperateincome18']>df01['ocftooperateincome17']
        df01["y"] = df01['ocftooperateincome17']>df01['ocftooperateincome16']
        df01["z"] = df01['ocftooperateincome16']>df01['ocftooperateincome15']
        df00["score2"] = df01.loc[:,["x","y","z"]].apply(lambda x: x.sum(), axis=1).replace([0, 1, 2, 3], [2, 3, 4.5, 5])
        df00["score"] = 0.6*df00["score0"]+0.2*df00["score1"]+0.2*df00["score2"]
        
        return df00.score

    def getEv(self,symbols,end_date=time.strftime('%Y%m%d',time.localtime())):
        print(self.getCurrentTime(),": get ev data from Wind Starting")
        data00 = w.wss(symbols,"ev","unit=1;tradeDate="+end_date+"")
        df00 = pd.DataFrame({'ev': data00.Data[0]},index=data00.Codes)
        df00.ev = df00.ev/100000000
        df00.fillna(0, inplace=True)
        df00.insert(1,'score0',1)        
        bins = [df00.ev.min(), 100, 200, df00.ev.max()]
        labels = [1, 4, 5]
        df00.loc[:,"score0"] = pd.cut(df00.ev, bins, labels = labels, include_lowest=True)
        df00.loc[:,"score0"] = df00['score0'].astype('int') 
        return df00.score0
# %% cell 2          
def main():
    '''
    主调函数，可以通过参数调整实现分批下载
    '''
    #global engine,sleep_time,symbols
    #sleep_time=1
    #engine = create_engine('mysql+pymysql://root:shang66@localhost:3306/invest?charset=utf8')
    #start_date='20100101'
    #end_date='20131231'
    #symbols=windStock.getAStockCodesFromCsv()#通过文件获取股票代码
    end_date=time.strftime('%Y%m%d',time.localtime())

    windStock=WindStock()
    symbols=windStock.getAStockCodesWind()
# 市值打分0.2
    s0 = windStock.getEv(symbols,end_date) #
#成长估值（32%）
    ##一致预测（20%）
    s1 = windStock.getPrediction(symbols,end_date) #
    ##估值指标30%
    s2 = windStock.getValuation(symbols,end_date) #
    ##成长指标（40%）
    s3 = windStock.getGrow(symbols)
    ##股息率（10%）
    s4 = windStock.getDividend(symbols,end_date) #
#盈利能力（32%）
    ##roe(65%)0.52
    s5 = windStock.getRoe(symbols)
    ##净利率（20%）0.16
    s6 = windStock.getNetprofit(symbols)
    ##毛利率（15%）0.12
    s7 = windStock.getGrossprofit(symbols)
    ##扣非净利/归母净利
    #0.2
    s8 = windStock.getDeductedprofit(symbols)
#现金流（16%）
    ##销售商品提供劳务收到的现金/营业收入
    s9 = windStock.getCashin(symbols)
    ##经营活动产生的现金流量净额/经营活动净收益(ocftooperateincome)
    s10 = windStock.getIncome(symbols)
      
    #[0.2,0.32*0.2,0.32*0.3,0.32*0.4,0.32*0.1,0.32*0.52,0.32*0.16,0.32*0.12,0.32*0.2,0.16*0.5,0.16*0.5]
    df_score = pd.DataFrame({'s0': s0,'s1': s1,'s2': s2,'s3': s3,'s4': s4,'s5': s5,'s6': s6,'s7': s7,'s8': s8,'s9': s9,'s10': s10})
    df_score["score"] = df_score.apply(lambda x: sum(x*[0.2,0.064,0.096,0.128,0.032,0.1664,0.0512,0.0384,0.064,0.08,0.08]), axis=1)
    name = 'Result'+end_date+'.csv'                    #定义文件名字  
    print(os.path.join(root, name))   #合并路径名字和文件名字，并打印
    df_score.to_csv(os.path.join(root, name),float_format='%.5f')

# %% cell 3 
def test():
    '''
    测试脚本，新增和优化功能时使用
    '''
    symbol='000001.SZ'
    end_date='20190628'
    #w.start();
    #stock=w.wsd(symbol,'trade_code,open,high,low,close')
    #stock=w.wsd(symbol, "trade_status,open,high,low,close,pre_close,volume,amt,dealnum,chg,pct_chg,vwap, adjfactor,close2,turn,free_turn,oi,oi_chg,pre_settle,settle,chg_settlement,pct_chg_settlement, lastradeday_s,last_trade_day,rel_ipo_chg,rel_ipo_pct_chg,susp_reason,close3, pe_ttm,val_pe_deducted_ttm,pe_lyr,pb_lf,ps_ttm,ps_lyr,dividendyield2,ev,mkt_cap_ard,pb_mrq,pcf_ocf_ttm,pcf_ncf_ttm,pcf_ocflyr,pcf_nflyr", start_date,end_date)
    #stock=w.wsd("000001.SZ", "pre_close,open,high,low,close,volume,amt,dealnum,chg,pct_chg,vwap,adjfactor,close2,turn,free_turn,oi,oi_chg,pre_settle,settle,chg_settlement,pct_chg_settlement,lastradeday_s,last_trade_day,rel_ipo_chg,rel_ipo_pct_chg,trade_status,susp_reason,close3", "2016-12-09", "2017-01-07", "adjDate=0")
    #print (stock)
 

         
         
         
if __name__ == "__main__":
    main()
