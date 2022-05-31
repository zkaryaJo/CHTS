import pybithumb

#2. 매도조건 달성여부 확인
def is_sell(bithumb, ticker, currPrice, avgBuyPrice):

    df = pybithumb.get_ohlcv(ticker)

    # yOpen = df.iloc[-2]['open']
    # yHigh = df.iloc[-2]['high']
    # yLow = df.iloc[-2]['low']
    # yClose = df.iloc[-2]['close']
    # yVolume = df.iloc[-2]['volume']

    # tOpen = df.iloc[-1]['open']
    tHigh = df.iloc[-1]['high']
    # tLow = df.iloc[-1]['low']
    # tClose = df.iloc[-1]['close']
    # tVolume = df.iloc[-1]['volume']



    if currPrice > avgBuyPrice :
        #평균 매입단가 대비 3%이상 상승 고점대비 3%이상 하락
        if (
            is_up_by_average_buy_price_percent(avgBuyPrice, currPrice , 3) and 
            is_down_by_high_price_percent(tHigh, currPrice, 2)
        ): 
            print('트레일링스탑')
            return True
    else:
        #손절
        if is_down_by_average_buy_price_percent(avgBuyPrice, currPrice , 2):
            print('손절')
            return True

    return False


#2-1 평균매입단가 대비 몇% 이상 상승
def is_up_by_average_buy_price_percent(avgBuyPrice, currPrice, percent=3):
    if (currPrice - avgBuyPrice) / currPrice >= percent :
        return True

    return False

#2-2 고점대비 몇% 이상 하락
def is_down_by_high_price_percent(tHigh, currPrice, percent=3):
    
    if (tHigh - currPrice) / tHigh >= percent :
        return True

    return False

#2-2 평균매입단가 대비 몇% 이상 하락
def is_down_by_average_buy_price_percent(avgBuyPrice, currPrice, percent=2):
    if (avgBuyPrice - currPrice) / avgBuyPrice >= percent :
        return True

    return False