import sys, datetime, time
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from pybithumb import *
from volatility import *

form_class = uic.loadUiType("resource/main.ui")[0]

class VolatilityWorker(QThread):
    tradingSent = pyqtSignal(str, str, str)

    def __init__(self, ticker, bithumb):
        super().__init__()
        self.ticker = ticker
        self.bithumb = bithumb
        self.alive = True

    def run(self):
        now = datetime.datetime.now()
        mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
        ma5 = get_yesterday_ma5(self.ticker)
        target_price = get_target_price(self.ticker)
        wait_flag = False
        
        #출력1
        self.tradingSent.emit(''+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "1_target_price", str(target_price))

        while self.alive:
            try:
                now = datetime.datetime.now()
                if mid < now < mid + datetime.delta(seconds=10):
                    target_price = get_target_price(self.ticker)
                    
                    #출력2
                    self.tradingSent.emit(''+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "1_target_price", str(target_price))

                    mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
                    ma5 = get_yesterday_ma5(self.ticker)
                    desc = sell_crypto_currency(self.bithumb, self.ticker)

                    result = self.bithumb.get_order_completed(desc)
                    timestamp = result['data']['order_date']
                    dt = datetime.datetime.fromtimestamp( int(int(timestamp)/1000000) )
                    tstring = dt.strftime("%Y/%m/%d %H:%M:%S")
                    self.tradingSent.emit(tstring, "매도", result['data']['order_qty'])
                    wait_flag = False

                if wait_flag == False:
                    current_price = pybithumb.get_current_price(self.ticker)
                    
                    #출력3
                    self.tradingSent.emit(''+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "2_current_price", str(current_price))
                    self.tradingSent.emit(''+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "2_target_price", str(target_price))
                    self.tradingSent.emit(''+datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "2_ma5", str(ma5))

                    if (current_price > target_price) and (current_price > ma5):
                        desc = buy_crypto_currency(self.bithumb, self.ticker)
                        result = self.bithumb.get_order_completed(desc)
                        timestamp = result['data']['order_date']
                        dt = datetime.datetime.fromtimestamp( int(int(timestamp)/1000000))
                        tstring = dt.strftime("%Y/%m/%d %H:%M:%S")
                        self.tradingSent.emit(tstring, "매수", result['data']['order_qty'])
                        wait_flag = True
            except:
                pass
            time.sleep(1)

    def close(self):
        self.alive = False



class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ticker = "PLA"
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
                balance = self.bithumb.get_balance(self.ticker)
                if balance == None:
                    self.textEdit.append("KEY가 올바르지 않습니다.")
                    return

            self.button.setText("매매중지")
            self.textEdit.append("------ START ------")
            self.textEdit.append(f"보유 현금 : {balance[2]} 원") 

            self.vw = VolatilityWorker(self.ticker, self.bithumb)
            self.vw.tradingSent.connect(self.receiveTradingSignal)
            self.vw.start()
        else:
            self.textEdit.append("------- END -------")
            self.button.setText("매매시작")
            self.vw.close()
        
    def receiveTradingSignal(self, time, type, amount):
        self.textEdit.append(f"[{time}] {type} : {amount}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())
        
    
    