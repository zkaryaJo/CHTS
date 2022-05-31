import sys, datetime, time
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from pybithumb import *
from buy import *
from sell import *
from common import *

form_class = uic.loadUiType("resource/main.ui")[0]

class BuyCondition:
    def __init__(self, a):
        self.a = a
    
class SellCondition:
    def __init__(self, a):
        self.a = a

class CustomWorker(QThread):
    mockTradingSent = pyqtSignal(str, str, str, str, str)
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
                for self.ticker in self.tickers :
                    try:
                        strTicker = self.ticker
                        self.balance = self.bithumb.get_balance(strTicker)
                        
                        tstring = get_now_to_string()
                        currPrice = get_current_price(strTicker)
                     
                        if currPrice is not None : 

                            #0. 내가 가진 코인 List에 추가
                            if  self.balance[0] is not None and self.balance[0] != 0 and (strTicker not in self.myCoinList):
                                self.tradingSent.emit(tstring, 'LOG', strTicker, str(currPrice), str(self.balance[0]))
                                self.myCoinList[strTicker] = (900, self.balance[0])

                            #1. 매수
                            if strTicker not in self.myCoinList:
                                if is_buy(self.bithumb, strTicker, currPrice):
                                    #desc = buy_crypto_currency(self.bithumb, self.ticker)
                                    #result = self.bithumb.get_order_completed(desc)
                                    #self.tradingSent.emit(get_timestamp_to_string(result['data']['order_date']), "임시매수", result['data']['order_qty'])
                                    #self.tradingSent.emit(tstring, "매수", result['data']['order_qty'])         
                                    self.tradingSent.emit(tstring, '임시매수', strTicker, str(currPrice), str(self.balance[0]))
                                    self.myCoinList[strTicker] = (currPrice, 1)
                                    continue

                            #2. 매도
                            if strTicker in self.myCoinList:
                                if is_sell(self.bithumb, strTicker, currPrice, self.myCoinList[strTicker][1]):
                                    #desc = sell_crypto_currency(self.bithumb, self.ticker)
                                    #result = self.bithumb.get_order_completed(desc)
                                    #self.tradingSent.emit(get_timestamp_to_string(result['data']['order_date']), "매도", result['data']['order_qty'])
                                    self.tradingSent.emit(tstring, '임시매도', strTicker, str(currPrice), str(self.balance[0]))
                            
                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)

    def close(self):
        self.alive = False



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

            self.cw = CustomWorker(self.bithumb)
            self.cw.tradingSent.connect(self.receiveTradingSignal)
            self.cw.start()
        else:
            self.textEdit.append("------- END -------")
            self.button.setText("매매시작")
            self.cw.close()
        
    def receiveTradingSignal(self, time, buyOrSellType, ticker, price, count):
        self.textEdit.append(f"[{time}] [{buyOrSellType}] [{ticker}], {price} * {count}개")
        self.ticker = ticker

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())
        
    
    