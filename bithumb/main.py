import sys, datetime, time
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from pybithumb import *
from custom import *

form_class = uic.loadUiType("resource/main.ui")[0]

class BuyCondition:
    def __init__(self, a):
        self.a = a
    
class SellCondition:
    def __init__(self, a):
        self.a = a

class CustomWorker(QThread):
    tradingSent = pyqtSignal(str, str, str)

    def __init__(self, bithumb):
        super().__init__()
        self.bithumb = bithumb
        self.alive = True

    def run(self):

        try:
            while self.alive:

                self.tickers = get_tickers()

                for self.ticker in self.tickers :
                    self.balance = self.bithumb.get_balance(str(self.ticker))
                    tstring = get_now_to_string()

                    self.currPrice = get_current_price(self.ticker)
                    #self.tradingSent.emit(tstring, "ticker", str(self.ticker)+', '+str(self.currPrice) + ', available:'+str(self.balance[0]))

                    #1. 매수
                    if is_buy(self.bithumb, self.ticker, self.currPrice):
                        
                        #desc = buy_crypto_currency(self.bithumb, self.ticker)
                        #result = self.bithumb.get_order_completed(desc)
                        #self.tradingSent.emit(get_timestamp_to_string(result['data']['order_date']), "임시매수", result['data']['order_qty'])
                        #self.tradingSent.emit(tstring, "매수", result['data']['order_qty'])                    
                        self.tradingSent.emit(tstring, "임시매수", get_current_price(self.ticker))
                    
                    if is_sell(self.bithumb, self.ticker, self.currPrice):
                        #desc = sell_crypto_currency(self.bithumb, self.ticker)
                        #result = self.bithumb.get_order_completed(desc)
                        #self.tradingSent.emit(get_timestamp_to_string(result['data']['order_date']), "매도", result['data']['order_qty'])
                        self.tradingSent.emit(tstring, "임시매도", str(get_current_price(self.ticker)))
                    
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
        
    def receiveTradingSignal(self, time, type, amount):
        self.textEdit.append(f"[{time}] {type} : {amount}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())
        
    
    