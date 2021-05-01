# encoding:utf-8


import re
import json
import hashlib
from numpy.core.numeric import cross
import requests
import traceback
from fake_useragent import UserAgent
from requests import RequestException
import time
import random
import itertools
import pandas as pd


class CtripSpider:

    def __init__(self, depCode, arrCode, date, adult=1, child=0, infant=0):

        self.depCode = depCode
        self.arrCode = arrCode
        self.date = date
        self.adult = adult
        self.child = child
        self.infant = infant
        self.headers = {'User-Agent': UserAgent().random}

    def getTransactionId(self):
        """获取transactionId and Params"""
        url = 'https://flights.ctrip.com/international/search/oneway-{}-{}?depdate={}&cabin=y_s&adult={}&child={}&infant={}'.format(
            self.depCode, self.arrCode, self.date, self.adult, self.child, self.infant)
        print(url)
        transactionId, data = None, None
        for _ in range(3):
            try:
                response = requests.get(url, headers=self.headers)
                data = re.findall(r'GlobalSearchCriteria =(.+);', response.text)[0].encode('utf-8')
                transactionId = json.loads(data).get("transactionID")
                return transactionId, data
            except:
                traceback.print_exc()
                continue
        print(transactionId, data)
        return transactionId, data

    def getSign(self, transactionId):
        sign_value = transactionId + self.depCode + self.arrCode + self.date
        # 进行md5加密
        _sign = hashlib.md5()
        _sign.update(sign_value.encode('utf-8'))

        headers = {
            'origin': "https://flights.ctrip.com",
            'sign': _sign.hexdigest(),
            'transactionid': transactionId,
            'Host': "flights.ctrip.com",
            'content-type': "application/json;charset=UTF-8",
        }
        self.headers.update(headers)

    # 请求并获取响应,获取源代码
    def get_information_page(self, data):
        """

        :return:
        """
        while True:
            try:
                requests.packages.urllib3.disable_warnings()
                res = requests.post(
                    url="https://flights.ctrip.com/international/search/api/search/batchSearch",
                    headers=self.headers,
                    data=data,
                    proxies=None,
                    timeout=5
                )
            except RequestException:
                # todo 请求抛错未处理 可能为代理网路延迟问题
                time.sleep(random.randint(1, 2))
                continue
            except Exception as e:
                # 其他未知错误
                print(e)
            else:
                print('else')
                # res.encoding = 'utf-8'
                # print(res.json())
                if res.json().get("data").get("context").get("searchCriteriaToken"):
                    return res.json()
                else:
                    return res.json()

    def main(self):
        transactionId, data = self.getTransactionId()
        if transactionId:
            self.getSign(transactionId)
            return self.get_information_page(data)
        else:
            print('no data')
            # print("账号被封禁")
            return None

'''
北京	BEIJING	PEK
上海	SHANGHAI	SHA
天津	TIANJIN	TSN
西安	XIAN	SIA
杭州	HANGCHOW	HGH
大連	DALIAN	DLC
青島	TSINGTAO	TAO
福州	FOOCHOW	FOC
廈門	XIAMEN	XMN
昆明	KUNMING	KMG
南京	NANKING	NKG
汕頭	SWATOW	SWA
桂林	GUILIN	KWL
成都	CHENGTU	CTU
廣州	CANTON	CAN
海口	HAIKOU	HAK
長沙	CHANGSHA	CSX
煙台	YANTAI	YNT
重慶	CHONGQING	CKG
溫州	WENZHOU	WNZ
三亞	SANYA	SYX
哈爾濱	HARBIN	HRB
深圳	SHENGZHEN	SZX
南昌	NANCHANG	KHN
東京	TOKYO	TYO
大阪	OSAKA	OSA
名古屋	NAGOYA	NGO
札幌	SAPPORO	SPK
福岡	FUKUOKA	FUK
沖繩	OKINAWA	OKA
漢城	SEOUL	SEL
釜山	PUSAN	PUS

'''
if __name__ == '__main__':
    start = '2021-06-15'
    end = '2021-08-17'
    date_list = pd.date_range(start,end).strftime("%Y-%m-%d").to_list()
    start_city = 'OSA'
    end_city = 'CAN'
    start_city_list = ['OSA','TYO']
    end_city_list = ['PEK','SHA','SZX','CZX','CAN','KHN','NKG','HGH','TAO','FOC','XMN','KMG','SWA','CTU','HAK','CSX','YNT','CKG','WNZ','SYX']
    ad_list = list(itertools.product(start_city_list,end_city_list))
    # date = '2021-06-17'
    df_empty = pd.DataFrame()
    for date in date_list: #循环天，最后再加不然太多几把了
        for aa in ad_list:
            spider = CtripSpider(aa[0],aa[1] , date)
            flight_info = spider.main()
            if flight_info and flight_info['msg'] == 'success' and len(flight_info['data'])>2:
                print('success')
                data = flight_info.get('data')
                flightItineraryList = data.get('flightItineraryList') #这里不确定是不是有多趟
                for itineraryId in flightItineraryList: #航线，即班次
                    flightSegments = itineraryId.get('flightSegments')   #飞行段，如果有多段会在这里展示
                    for flight in flightSegments:
                        airlineCode = flight.get('airlineCode') #航班编号？
                        airlineName = flight.get('airlineName') #航班公司名
                        crossDays = flight.get('crossDays') #跨天
                        transferCount = flight.get('transferCount') #换线次数
                        stopCount = flight.get('stopCount') #停靠次数
                        duration = flight.get('duration') #时长（分钟）
                        flightList = flight.get('flightList') #估计是航班数大于2时候会多出来
                        for Flight in flightList:
                            nf = pd.DataFrame([Flight])
                            nf['airlineCode'] = airlineCode
                            nf['airlineName'] = airlineName
                            nf['crossDays'] = crossDays
                            nf['transferCount'] = transferCount
                            nf['stopCount'] = stopCount
                            nf['duration'] = duration
                            df_empty = df_empty.append(nf)
                            
                    priceList = itineraryId.get('priceList')
                    for price in priceList:
                        pricedf = pd.DataFrame([price])
                        df_empty = df_empty.append(pricedf)
            else:
                pass
                
    # print(df_empty)
    df_empty.to_excel('airline3.xlsx')
    # df_cc.to_excel('test2.xlsx')
