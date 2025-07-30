import pandas as pd
import numpy as np
import json
import requests
from pandas import json_normalize
from datetime import datetime

def top_stock(exchange,type):
    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }

    payload = {
        "columns": [
            "name",  # cổ phiếu
            "sector", # ngành
            "exchange", # sàn
            "close",  #giá
            "change", # thay đổi giá
            "volume", # KLGD
            "volume_change", #Thay đổi KLGD #ở đâu ra
            "market_cap_basic", #vốn hóa
            "price_earnings_ttm", #P/E raito
            "earnings_per_share_diluted_ttm", #EPS 
            "relative_volume_10d_calc", #KLTB 10 ngày
            "dividends_yield_current", #Tỷ suất cổ tức
            "total_revenue_ttm", #tổng doanh thu
            "earnings_per_share_diluted_yoy_growth_ttm", # doanh thu tăng trưởng
            "oper_income_ttm", # Lợi nhuận hoạt động(năm)
            "net_income_ttm" #LNST
            ],
        "ignore_unknown_fields": False,
        "markets": ["vietnam"],
        "options": {"lang": "en"},
        "range": [0, 1600],
        "sort": {"sortBy": "market_cap_basic","sortOrder": "desc"}
        
    }

    url = "https://scanner.tradingview.com/vietnam/scan"
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    data = response.json()
    datax=pd.json_normalize(data['data'])
    datay=datax.drop(columns='s')
    df_data=pd.DataFrame(datay['d'].to_list())
    df_data.columns = [
    "Cổ phiếu", "Ngành", "Sàn", "Giá", "Thay đổi(%)", "Khối lượng", "Khối lượng(%)", "Vốn hóa", "PE Ratio", "EPS", "KLTB 10 ngày", "Tỷ suất cổ tức(%)",
    "Tổng doanh thu", "Doanh thu tăng trưởng(%)", "Lợi nhuận hoạt động(năm)", "LNST"]
    df_data=df_data.fillna(0)
    cols=['Giá','Khối lượng','Vốn hóa','Tổng doanh thu','Lợi nhuận hoạt động(năm)','LNST']
    df_data[cols]=df_data[cols].astype(int)

    if exchange=='HOSE':
        if type=='up':
            return df_data[df_data['Sàn']=='HOSE'].sort_values("Thay đổi(%)",ascending=False).iloc[:10].style.format({col:"{:,}" for col in cols})
        else: 
            return df_data[df_data['Sàn']=='HOSE'].sort_values("Thay đổi(%)",ascending=True).iloc[:10].style.format({col:"{:,}" for col in cols}) 
    elif exchange=='HNX':
        if type=='up':
            return df_data[df_data['Sàn']=='HNX'].sort_values("Thay đổi(%)",ascending=False).iloc[:10].style.format({col:"{:,}" for col in cols})
        else: 
            return df_data[df_data['Sàn']=='HNX'].sort_values("Thay đổi(%)",ascending=True).iloc[:10].style.format({col:"{:,}" for col in cols}) 
    elif exchange=='UPCOM':
        if type=='up':
            return df_data[df_data['Sàn']=='UPCOM'].sort_values("Thay đổi(%)",ascending=False).iloc[:10].style.format({col:"{:,}" for col in cols})
        else: 
            return df_data[df_data['Sàn']=='UPCOM'].sort_values("Thay đổi(%)",ascending=True).iloc[:10].style.format({col:"{:,}" for col in cols}) 
