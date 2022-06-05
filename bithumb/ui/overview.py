import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *
from pybithumb import WebSocketManager

class OverViewWorker(QThread):
    #dataSent = pyqtSignal(int, float, float, int, float, int, float, int)
    data24Sent = pyqtSignal(float, float, float, float, float, float)
    dataMidSent = pyqtSignal(float, float, float)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True

    def run(self):
        wm = WebSocketManager("ticker", [f"{self.ticker}_KRW"], ["24H", "MID"])
        while self.alive:
            data = wm.get()
            
            if data is not None :
                if data['content']['tickType'] == "MID":
                    self.dataMidSent.emit(float(data['content']['closePrice' ]),
                                        float(data['content']['chgRate'    ]),
                                        float(data['content']['volumePower']))
                else:
                    self.data24Sent.emit(float(data['content']['closePrice'    ]),
                                        float (data['content']['volume'        ]),
                                        float (data['content']['highPrice'     ]),
                                        float (data['content']['value'         ]),
                                        float (data['content']['lowPrice'      ]),
                                        float (data['content']['prevClosePrice']))

    def close(self):
        self.alive = False

class OverviewWidget(QWidget):
    def __init__(self, parent=None, ticker="BTC"):
        super().__init__(parent)
        uic.loadUi("resource/overview.ui", self)
        self.ticker = ticker
        
        self.ovw = OverViewWorker(ticker)
        self.ovw.data24Sent.connect(self.fill24Data)
        self.ovw.dataMidSent.connect(self.fillMidData)
        self.ovw.start()

    def changeTicker(self, ticker='BTC'):
        self.ovw.close()
        self.ticker = ticker
        self.ovw = OverViewWorker(ticker)
        self.ovw.data24Sent.connect(self.fill24Data)
        self.ovw.dataMidSent.connect(self.fillMidData)
        self.ovw.start()

    def fillData(self, currPrice, chgRate, volume, highPrice, value, lowPrice, volumePower, prevClosePrice):
        self.label_1.setText(f"{currPrice:,.4f}")
        self.label_2.setText(f"{chgRate:+.2f}%")
        self.label_15.setText(f"{volume:.4f} {self.ticker}")
        self.label_6.setText(f"{highPrice:,.4f}")
        self.label_8.setText(f"{value/100000000:,.1f} 억")
        self.label_10.setText(f"{lowPrice:,.4f}")
        self.label_12.setText(f"{volumePower:.2f}%")
        self.label_14.setText(f"{prevClosePrice:,.4f}")

    def fill24Data(self, currPrice, volume, highPrice, value, lowPrice, prevClosePrice):
        self.label_1.setText(f"{currPrice:,.4f}")
        self.label_15.setText(f"{volume:.4f} {self.ticker}")
        self.label_6.setText(f"{highPrice:,.4f}")
        self.label_8.setText(f"{value/100000000:,.1f} 억")
        self.label_10.setText(f"{lowPrice:,}")
        self.label_14.setText(f"{prevClosePrice:,.4f}")
        self.__updateStyle()

    def fillMidData(self, currPrice, chgRate, volumePower):
        self.label_1.setText(f"{currPrice:,.4f}")
        self.label_2.setText(f"{chgRate:+.2f}%")
        self.label_12.setText(f"{volumePower:.2f}%")
        self.__updateStyle()

    def closeEvent(self, event):
        self.ovw.close()

    def __updateStyle(self): #스타일 업데이트
        if '-' in self.label_2.text():
            self.label_1.setStyleSheet("color:blue;")
            self.label_2.setStyleSheet("background-color:blue;color:white")
        else:
            self.label_1.setStyleSheet("color:red;")
            self.label_2.setStyleSheet("background-color:red;color:white")


# if __name__ == "__main__":
#     import sys
#     from PyQt5.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     ob = OverviewWidget()
#     ob.show()
#     exit(app.exec_())