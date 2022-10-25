import os, sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QValidator
from PyPDF2 import PdfReader, PdfMerger
import re
from GUI.ui_pdfmerger import *

class DlgMain(QDialog,Ui_dlgMerge):
    def __init__(self):
        super(DlgMain,self).__init__()
        self.setupUi(self)
        self.setLayout(self.lytMain) # Set main layout. The program can now stretch
        self.btgPages = QButtonGroup()
        self.btgPages.addButton(self.rbtAllPages)
        self.btgPages.addButton(self.rbtSelectedPages)
        self.btgPages.setId(self.rbtAllPages,1)
        self.btgPages.setId(self.rbtSelectedPages,0)

        self.Files = [] # Initial constructor for PDF files. When adding to to the list widget, the PDF is appended here as well as a dictionary.
        self.ledOutputFilepath.setText(os.getcwd() + "\\" + self.ledOutputFilepath.text())
        self.OutputFilepathMerged = self.ledOutputFilepath.text()

        # Signals and slots
        ## "Files to merge" group
        self.btnAddFiles.clicked.connect(self.evt_btnAddFiles_clicked) # Add files button
        self.btnRemoveFiles.clicked.connect(self.evt_btnRemoveFiles_clicked)
        self.btnDocDown.clicked.connect(self.evt_btnDocDown_clicked)
        self.btnDocUp.clicked.connect(self.evt_btnDocUp_clicked)
        self.lbxFiles.itemClicked.connect(self.evt_lbxFiles_itemClicked)

        ## "File properties" group
        self.rbtAllPages.clicked.connect(self.evt_btgPages_clicked)
        self.rbtSelectedPages.clicked.connect(self.evt_btgPages_clicked)
        self.ledSetDocPages.editingFinished.connect(self.evt_ledSetDocPages_editingFinished)

        ## Output filename
        self.ledOutputFilepath.textChanged.connect(self.evt_ledOutputFilepath_textChanged)
        self.btnOutputMergedFile.clicked.connect(self.evt_btnOutputMergedFile_clicked)

        ## 'Start merging' button
        self.btnMerge.clicked.connect(self.evt_btnMerge_clicked)

    def evt_btnAddFiles_clicked(self):
        filepath, filter = QFileDialog.getOpenFileName(self,'Open','',filter='PDF (*.pdf)')
        if filepath:
            addFile = True
            filepaths = [x['filepath'] for x in self.Files]
            if filepath in filepaths:
            # if filepath in self.Files:
                msg = QMessageBox.question(self,'File already added','File already added. Add it again?')
                if msg == QMessageBox.No:
                    addFile = False

            if addFile:
                pdfFile = PdfReader(filepath)
                noPages = len(pdfFile.pages)

                filename = os.path.basename(filepath)
                fileDict = {
                    'filename': filename,
                    'filepath': filepath,
                    'pages':noPages,
                    'mergePages': f'{0}-{noPages}',
                }
                self.Files.append(fileDict)
                
                self.lbxFiles.addItem(filename)

        if self.lbxFiles.count() > 1:
            self.btnMerge.setEnabled(True)

    def evt_btnRemoveFiles_clicked(self):
        lstItems = self.lbxFiles.selectedItems()
        for itm in lstItems:
            QLWIrow = self.lbxFiles.row(itm)
            QLWI = self.lbxFiles.takeItem(QLWIrow)
            if self.lbxFiles.count() in (0,1):
                self.btnDocUp.setEnabled(False)
                self.btnDocDown.setEnabled(False)
            elif self.lbxFiles.count() > 1:
                if QLWIrow == 0:
                    self.btnDocUp.setEnabled(False)
                elif QLWIrow == self.lbxFiles.count()-1:
                    self.btnDocDown.setEnabled(False)
            del self.Files[QLWIrow]

        if self.lbxFiles.count() < 2:
            self.btnStartMerge.setEnabled(False)
            self.prgMerging.setEnabled(False)

    def evt_btnDocDown_clicked(self):
        lstItems = self.lbxFiles.selectedItems()
        for itm in lstItems:
            QLWIrow = self.lbxFiles.row(itm)
            QLWI = self.lbxFiles.takeItem(QLWIrow)
            self.lbxFiles.insertItem(QLWIrow+1,itm)
            self.lbxFiles.setCurrentRow(QLWIrow+1)

            fileDict = self.Files[QLWIrow]
            self.Files.insert(QLWIrow+1,self.Files.pop(self.Files.index(fileDict)))

    def evt_btnDocUp_clicked(self):
        lstItems = self.lbxFiles.selectedItems()
        for itm in lstItems:
            QLWIrow = self.lbxFiles.row(itm)
            QLWI = self.lbxFiles.takeItem(QLWIrow)
            self.lbxFiles.insertItem(QLWIrow-1,itm)
            self.lbxFiles.setCurrentRow(QLWIrow-1)

            fileDict = self.Files[QLWIrow]
            self.Files.insert(QLWIrow-1,self.Files.pop(self.Files.index(fileDict)))

    def evt_lbxFiles_itemClicked(self,itm):
        QLWIrow = self.lbxFiles.row(itm)
        
        fileDict = self.Files[QLWIrow]
        NoPagesText = f'Number of pages: {fileDict["pages"]}'
        self.lblNoDocPages.setText(NoPagesText)
        self.ledSetDocPages.setText(fileDict['mergePages']) # Write page numbers

        # Up and down button changes
        if self.lbxFiles.count() > 1:
            if QLWIrow == 0:
                self.btnDocDown.setEnabled(True)
                self.btnDocUp.setEnabled(False)
            elif QLWIrow == self.lbxFiles.count()-1:
                self.btnDocDown.setEnabled(False)
                self.btnDocUp.setEnabled(True)
            else:
                self.btnDocDown.setEnabled(True)
                self.btnDocUp.setEnabled(True)

        self.btnRemoveFiles.setEnabled(True)
        self.grpFileProperties.setEnabled(True)

    def evt_btgPages_clicked(self):
        btgID = self.btgPages.id(self.btgPages.checkedButton())
        if btgID == 0:
            self.ledSetDocPages.setEnabled(True)
        else:
            self.ledSetDocPages.setEnabled(False)

            curRow = self.lbxFiles.currentRow()
            curDocPages = self.Files[curRow]['pages']
            newText = '0-' + str(curDocPages)      
            self.Files[curRow]['mergePages'] = newText
            self.ledSetDocPages.setText(newText)
    
    
    def evt_ledSetDocPages_editingFinished(self):
        curRow = self.lbxFiles.currentRow()
        curDocPages = self.Files[curRow]['pages']

        pagesText = self.ledSetDocPages.text()
        srcPattern = r'\s?(\d+)\s?-\s?(\d+)\s?|\s?(\d+)\s?'
        textList = re.findall(srcPattern,pagesText)

        newPagesTextLst = []
        for txt in textList:
            includeText = ''
            if txt[0] and txt[1]:
                if int(txt[0]) <= curDocPages and int(txt[1]) <= curDocPages and int(txt[0]) < int(txt[1]):
                    includeText += txt[0] + '-' + txt[1]
            else:
                if int(txt[2]) <= curDocPages:
                    includeText += txt[-1]
            if includeText:
                newPagesTextLst.append(includeText)
        newPagesText = ','.join(newPagesTextLst)
        self.ledSetDocPages.setText(newPagesText)

        self.Files[curRow]['mergePages'] = newPagesText

    def evt_ledOutputFilepath_textChanged(self,text):
        filepath, fileExt = os.path.splitext(text)
        if fileExt != '.pdf':
            text = filepath + '.pdf'
        self.OutputFilepathMerged = text
    
    def evt_btnOutputMergedFile_clicked(self):
        filepath, filter = QFileDialog.getSaveFileName(self,'Save as','',filter='PDF (*.pdf)')
        if filepath:
            self.ledOutputFilepath.setText(filepath)
    
    def evt_btnMerge_clicked(self):
        cmbLayoutTxt = self.cmbPageLayout.currentText()
        cmbLayoutTxtLst = cmbLayoutTxt.split(' ')
        LayoutText = '/' + ''.join(cmbLayoutTxtLst)
        print(LayoutText)

        merger = PdfMerger()
        merger.set_page_layout(LayoutText)
        for pdf in self.Files:
            srcPattern = r'\s?(\d+)\s?-\s?(\d+)\s?|\s?(\d+)\s?'
            pagesText = pdf['mergePages']
            textList = re.findall(srcPattern,pagesText)
            input = open(pdf['filepath'],'rb')
            for txt in textList:
                if txt[0] and txt[1]:
                    pageStart = int(txt[0])
                    pageEnd = int(txt[1])
                else:
                    pageEnd = int(txt[2])
                    pageStart = int(txt[2])-1
                merger.append(fileobj=input,pages=(int(pageStart),int(pageEnd)))
            input.close()

        output = open(self.OutputFilepathMerged,'wb')
        merger.write(output)

        merger.close()
        output.close()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlgMain = DlgMain()
    dlgMain.show()
    sys.exit(app.exec_())