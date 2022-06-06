import datetime
import pybithumb
import logging
import json
import requests

#파라미터로 들어온 timeStamp를 현재시간으로
def get_timestamp_to_string(ts):
    return datetime.datetime.fromtimestamp(int(int(ts)/1000000)).strftime("%Y/%m/%d %H:%M:%S")

#현재시간 String으로 
def get_now_to_string():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

#구매
def buy_crypto_currency(bithumb, ticker):
    krw = bithumb.get_balance(ticker)[2]
    orderbook = pybithumb.get_orderbook(ticker)
    sell_price = orderbook['asks'][0]['price']
    unit = krw/float(sell_price) * 0.7
    return bithumb.buy_market_order(ticker, unit)
#판매
def sell_crypto_currency(bithumb, ticker):
    unit = bithumb.get_balance(ticker)[0]
    return bithumb.sell_market_order(ticker, unit)

def get_target_price(ticker):
    df = pybithumb.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    tOpen = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = tOpen + (yesterday_high - yesterday_low) * 0.5
    return target

def get_yesterday_ma5(ticker):
    df = pybithumb.get_ohlcv(ticker)
    close = df['close']
    ma = close.rolling(5).mean()
    return ma[-2]

#로그
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
log = logging.getLogger()
log.setLevel(logging.INFO)
file_handler = logging.FileHandler('log\logfile_{:%Y%m%d}.log'.format(datetime.datetime.now()), encoding='utf-8')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

#슬랙
webhook_url = "https://hooks.slack.com/services/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"

def pushToSlack(content):
    payload = {"text": content}
    try:
        requests.post(
            webhook_url, data=json.dumps(payload),headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        log.info(e)
