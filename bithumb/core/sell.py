import pybithumb
from core.common import *

#2. 매도조건 달성여부 확인
def is_sell(bithumb, ticker, currPrice, avgBuyPrice):

    try:
        df = pybithumb.get_ohlcv(ticker)

        if df is None :
            log.info('[ERR] is Sell response is Crashed')
            return False

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

        log.info('[Sell]\t'+"{:10}".format(ticker)+"{:25}".format("현재가:"+str(currPrice))+"{:5}".format("수량:1")+"{:25}".format("평균매수가:"+str(avgBuyPrice)))

        if currPrice > avgBuyPrice :
            #print('[+] 상승 - 트레일링스탑 확인필요 현재가: ', str(currPrice), ', 매수단가: ',str(avgBuyPrice))
            #평균 매입단가 대비 3%이상 상승 고점대비 3%이상 하락
            if (
                is_up_by_average_buy_price_percent(avgBuyPrice, currPrice , 3) and 
                is_down_by_high_price_percent(tHigh, currPrice, 2)
            ): 
                log.info('트레일링스탑')
                pushToSlack('[+]익절 trailing stop')
                return True
        elif currPrice < avgBuyPrice :
            #print('[-] 하락 - 손절여부 확인필요 현재가: ', str(currPrice), ', 매수단가: ',str(avgBuyPrice))
            #손절
            if is_down_by_average_buy_price_percent(avgBuyPrice, currPrice , 2):
                pushToSlack('[-]손절 stop loss')
                log.info('손절')
                return True
        else :
            return False

    except Exception as e:
        log.info(e)
        
    return False


#2-1 평균매입단가 대비 몇% 이상 상승
def is_up_by_average_buy_price_percent(avgBuyPrice, currPrice, percent=3):
    if (currPrice - avgBuyPrice) / avgBuyPrice * 100 >= percent :
        log.info('[Sell] > True > is_up_by_average_buy_price_percent')
        return True

    log.info('[Sell] > False > is_up_by_average_buy_price_percent')
    return False

#2-2 고점대비 몇% 이상 하락
def is_down_by_high_price_percent(tHigh, currPrice, percent=3):
    if (tHigh - currPrice) / tHigh * 100 >= percent :
        log.info('[Sell] > True > is_down_by_high_price_percent')
        return True
    log.info('[Sell] > False > is_down_by_high_price_percent')
    return False

#2-2 평균매입단가 대비 몇% 이상 하락
def is_down_by_average_buy_price_percent(avgBuyPrice, currPrice, percent=2):
    if (avgBuyPrice - currPrice) / avgBuyPrice * 100 >= percent :
        log.info('[Sell] > True > is_down_by_average_buy_price_percent')
        return True
    log.info('[Sell] > False > is_down_by_average_buy_price_percent')
    return False