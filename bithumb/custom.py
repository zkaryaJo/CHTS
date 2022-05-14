import time
import pybithumb

def get_target_price(ticker):
    df = pybithumb.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + (yesterday_high - yesterday_low) * 0.5
    return target



def is_all_condition_satisfied(ticker):
    df = pybithumb.get_ohlcv(ticker)
    
    if is_gap_up(df, 2) and is_low_down(df, 2) and 

    return false
    

#1. 갭상
def is_gap_up(df, percent=2):

    if percent < 0 and percent > 100 :
        return False

    yesterday_close = df.iloc[-2]['close']
    today_open = df.iloc[-1]['open']

    if (today_open - yesterday_close) / yesterday_close * 100 >= percent:
        return True
    
    return False


#-> 보류 ->> 당일 저가 2%이하 하락 
def is_low_down(df, percent=2):

    if percent < 0 and percent > 100 :
        return False

    yesterday_close = df.iloc[-2]['close']
    today_open = df.iloc[-1]['open']
    
    if (today_open - yesterday_close) / yesterday_close * 100 >= percent:
        return True
    
    return False

#3. 거래량 70% 이상
def is_volume_up(df, percent=70):

    if percent < 0 and percent > 100 :
        return False

    yesterday_volume = df.iloc[-2]['volume']
    today_volume = df.iloc[-1]['volume']
    
    if (today_volume - yesterday_volume) / yesterday_volume * 100 >= percent:
        return True
    
    return False

#4. 시가회복 
def is_market_price_recovery(df, percent=70):

    if percent < 0 and percent > 100 :
        return False

    yesterday_volume = df.iloc[-2]['volume']
    today_volume = df.iloc[-1]['volume']
    
    if (today_volume - yesterday_volume) / yesterday_volume * 100 >= percent:
        return True
    
    return False

#5. 거래대금 1분 1억이상

#6. 당일 20%이상 상승 제외

#7. 현재가가 최고가인 경우

#구매
def buy_crypto_currency(bithumb, ticker):
    krw = bithumb.get_balance(ticker)[2]
    orderbook = pybithumb.get_orderbook(ticker)
    sell_price = orderbook['asks'][0]['price']
    unit = krw/float(sell_price) * 0.7
    return bithumb.buy_market_order(ticker, unit)

def sell_crypto_currency(bithumb, ticker):
    unit = bithumb.get_balance(ticker)[0]
    return bithumb.sell_market_order(ticker, unit)

def get_yesterday_ma5(ticker):
    df = pybithumb.get_ohlcv(ticker)
    close = df['close']
    ma = close.rolling(5).mean()
    return ma[-2]