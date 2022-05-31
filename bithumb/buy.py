import pybithumb

#1. 구매조건 달성여부 확인
def is_buy(bithumb, ticker, currPrice):

    currPrice = float(currPrice)
    tk = pybithumb.get_ticker(ticker)['data']
    trade_value_24H = float(tk['acc_trade_value_24H']) #24시간 거래대금

    df = pybithumb.get_ohlcv(ticker)
    
    # yOpen = df.iloc[-2]['open']
    # yHigh = df.iloc[-2]['high']
    # yLow = df.iloc[-2]['low']
    # yClose = df.iloc[-2]['close']
    yVolume = df.iloc[-2]['volume']

    tOpen = df.iloc[-1]['open']
    tHigh = df.iloc[-1]['high']
    # tLow = df.iloc[-1]['low']
    # tClose = df.iloc[-1]['close']
    tVolume = df.iloc[-1]['volume']
    
    if ( #is_gap_up(tOpen, yClose, 2) and 
         #is_low_down(tOpen, currPrice, 2) and 
         is_volume_up(tVolume, yVolume, 70) and  
         is_market_price_recovery(currPrice, tOpen) and 
         is_up_trading_value_by_amount(trade_value_24H, minutes=60, amount=100000000) and
         is_up_by_open_price_percent(tOpen, currPrice, 20) and 
         is_market_price_highest(currPrice, tHigh)
    ): 
        return True

    return False
    
#1-1 갭상 대비 2%이상 - 
def is_gap_up(tOpen, yClose, percent=2):

    if percent < 0 and percent > 100 :
        return False

    #GAP : (금일시가-전일종가) / 전일종가 * 100
    if (tOpen - yClose) / yClose * 100 >= percent:
        return True
    
    return False

#1-2 보류 ->> 당일 저가 2%이하 하락 - 
def is_low_down(tOpen, currPrice, percent=2):

    if percent < 0 and percent > 100 :
        return False
    
    #if (tOpen - yClose) / yClose * 100 >= percent:
        #return True
    
    return False

#1-3 전일 대비 거래량 70% 이상
def is_volume_up(tVolume, yVolume, percent=70):

    if percent < 0 and percent > 100 :
        return False
    
    #금일 거래량 >= 전일 거래량 * percent / 전일 거래량
    if tVolume >= yVolume*percent / 100 :
        return True
    
    return False

#1-4 시가회복 
def is_market_price_recovery(currPrice, tOpen):
    
    if currPrice >= tOpen: 
        return True
    return False

#1-5 거래대금 1분 1억이상 
def is_up_trading_value_by_amount(trade_value_24H, minutes=60, amount=100000000):
    """
    :trade_value_24H - 최근 24시간 거래금액
    :amount - 입력할 거래대금
    :minutes - 입력할 시간(분단위)
    """
    if trade_value_24H / 24 / 60 * minutes >= amount :
        return True

    return False

#1-6 당일 20%이상 상승 제외
def is_up_by_open_price_percent(tOpen, currPrice, percent=20):
    
    if currPrice  <= tOpen + (tOpen * percent / 100)  :
        return True

    return False

#1-7 현재가가 최고가인 경우
def is_market_price_highest(currPrice, tHigh):
    if currPrice >= tHigh: 
        return True
    return False
