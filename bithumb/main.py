import sys, datetime, time
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from pybithumb import *
from core.buy import *
from core.sell import *
from core.common import *

form_class = uic.loadUiType("resource/main.ui")[0]

class BuyCondition:
    def __init__(self, a):
        self.a = a
    
class SellCondition:
    def __init__(self, a):
        self.a = a

class CustomWorker(QThread):
    tradingSent = pyqtSignal(str, str, str, str, str)

    def __init__(self, bithumb):
        super().__init__()
        self.bithumb = bithumb
        self.alive = True

    def run(self):

        self.myCoinList = {}

        while self.alive:
            try:
                self.tickers = get_tickers()

                for strTicker in self.tickers :
                    try:
                        
                        #1. 매도
                        for strSellMyTicker in self.myCoinList:
                            tstring = get_now_to_string()
                            currPrice = get_current_price(strSellMyTicker)
                            avgBuyPrice = self.myCoinList[strSellMyTicker][0]
                            count = self.myCoinList[strSellMyTicker][1]

                            if currPrice is not None and strSellMyTicker is not None : 
                                if is_sell(self.bithumb, strSellMyTicker, currPrice, avgBuyPrice):
                                    log.info('[+] 임시매도'+'\t'+strSellMyTicker+'\t'+str(currPrice)+'\t'+str(count))
                                    self.tradingSent.emit(tstring, '임시매도', strSellMyTicker, "매도:"+str(currPrice)+", 평균매수가:"+str(avgBuyPrice), str(count))
                                    self.myCoinList.pop(strSellMyTicker)
                        if strTicker is not None :
                            tstring = get_now_to_string()
                            currPrice = get_current_price(strTicker)
                            self.balance = self.bithumb.get_balance(strTicker)
                            
                            if currPrice is not None : 
                                #0. 내가 가진 코인 List에 추가
                                if  self.balance[0] is not None and self.balance[0] != 0 and (strTicker not in self.myCoinList):
                                    if strTicker == 'PLA' :
                                        pass
                                        #self.tradingSent.emit(tstring, 'LOG', strTicker, str(791.8), str(self.balance[0]))
                                        #self.myCoinList[strTicker] = (791.8, self.balance[0])
                                    else :
                                        self.tradingSent.emit(tstring, 'LOG', strTicker, str(currPrice), str(self.balance[0]))
                                        self.myCoinList[strTicker] = (currPrice, self.balance[0])

                                #1. 매수
                                if strTicker not in self.myCoinList:
                                    if is_buy(self.bithumb, strTicker, currPrice):
                                        log.info('[+] 임시매수'+'\t'+strTicker+'\t'+str(currPrice)+'\t'+str(1))
                                        self.tradingSent.emit(tstring, '임시매수', strTicker, str(currPrice), str(1))
                                        self.myCoinList[strTicker] = (currPrice, 1)                                
                                
                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)

    def close(self):
        self.alive = False
        pushToSlack("------- END -------")



class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ticker = "BTC"
        self.button.clicked.connect(self.clickBtn)

        with open("bithumb.txt") as f:
            lines = f.readlines()
            apikey = lines[0].strip()
            seckey = lines[1].strip()
            self.apiKey.setText(apikey)
            self.secKey.setText(seckey)
    
    def changeTicker(self, ticker):
        super().__init__(parent=None, ticker=ticker)
        self.setupUi(self)
        self.ticker = ticker
        self.button.clicked.connect(self.clickBtn)

    def clickBtn(self):
        if self.button.text() == "매매시작":
            apiKey = self.apiKey.text()
            secKey = self.secKey.text()
            if len(apiKey) != 32 or len(secKey) != 32:
                self.textEdit.append("KEY가 올바르지 않습니다.")
                return
            else:
                self.bithumb = Bithumb(apiKey, secKey)
                self.balance = self.bithumb.get_balance(self.ticker)
                if self.balance == None:
                    self.textEdit.append("KEY가 올바르지 않습니다.")
                    return

            self.button.setText("매매중지")
            self.textEdit.append("------ START ------")
            self.textEdit.append(f"보유 현금 : {self.balance[2]} 원")

            pushToSlack(f"------ START ------\n보유 현금 : {self.balance[2]} 원")

            self.cw = CustomWorker(self.bithumb)
            self.cw.tradingSent.connect(self.receiveTradingSignal)
            self.cw.start()
        else:
            self.textEdit.append("------- END -------")
            self.button.setText("매매시작")
            self.cw.close()
        
    def receiveTradingSignal(self, time, buyOrSellType, ticker, price, count):
        self.textEdit.append(f"[{time}] [{buyOrSellType}] [{ticker}] > {price} {count}개")
        pushToSlack(f"[{time}] [{buyOrSellType}] [{ticker}] > {price} {count}개")
        if ticker is not None:
            self.widget_ovv.changeTicker(ticker)  #overView
            self.widget_odb.changeTicker(ticker)  #orderbook
            self.widget_cht.changeTicker(ticker)  #chart

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())
        
    
    