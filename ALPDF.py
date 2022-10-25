import os, sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtCore import QUrl
from GUI.ui_ALPDF import *

class MenuMain(QMainWindow,Ui_MenuMain):
    def __init__(self):
        super(MenuMain,self).__init__()
        self.setupUi(self)
        self.setWindowTitle('AL PDF')

        self.wevPDF.settings().setAttribute(QWebEngineSettings.PluginsEnabled,True)

        # Signals
        self.actionOpen.triggered.connect(self.evt_openDoc_triggered)
    
    def evt_openDoc_triggered(self):
        sFile,sFilter = QFileDialog.getOpenFileName(self,'Open','',filter='PDF (*.pdf)')
        if sFile:
            url = QUrl.fromLocalFile(sFile)
            self.wevPDF.load(url)
            #print(sFile)
        else:
            print('Canceled by user!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mnuMain = MenuMain()
    mnuMain.show()
    sys.exit(app.exec_())