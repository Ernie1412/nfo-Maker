from PyQt5 import QtWidgets, uic, QtCore,QtGui
import os,sys,ssl,re,win32com.client,shutil,time,json
import pyperclip
from pathlib import Path
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


import Scraping
#import CheckableComboBox

Options = Options()
GECKO=r"E:\Python\Python_WORK\geckodriver.exe"
LAENDER_JSON_PATH = Path(__file__).absolute().parent / "JSON/laender.json"

##Firefox(options=Options,executable_path='E:/Python/Python379/Lib/site-packages/selenium/webdriver/firefox')
#Firefox().quit()
###-------------------------Option für firefox hide setzen(nicht sichtbar)---------###
### -------------------------------------------------------------------------------###
#
###--------------------------Globale variable--------------------------------------###

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self,parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QtGui.QStandardItemModel(self))       
  
    # when any item get pressed
    def handle_item_pressed(self, index):
  
        # getting which item is pressed
        item = self.model().itemFromIndex(index)
  
        # make it check if unchecked and vice-versa
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
  
        # calling method
        self.check_items()
  
    # method called by check_items
    def item_checked(self, index):
  
        # getting item at index
        item = self.model().item(index, 0)
  
        # return true if checked else false
        return item.checkState() == QtCore.Qt.Checked
  
    # calling method
    def check_items(self):
        # blank list
        checkedItems = []
  
        # traversing the items
        for i in range(self.count()):
  
            # if item is checked add it to the list
            if self.item_checked(i):
                checkedItems.append(i)
  
        # call this method
        self.update_labels(checkedItems)
  
    # method to update the label
    def update_labels(self, item_list):
  
        n = ''
        count = 0
  
        # traversing the list
        for i in item_list:
  
            # if count value is 0 don't add comma
            if count == 0:
                n += ' % s' % i
            # else value is greater then 0
            # add comma
            else:
                n += ', % s' % i
  
            # increment count
            count += 1
  
  
        # loop
        for i in range(self.count()):
  
            # getting label
            text_label = self.model().item(i, 0).text()
  
            # default state
            if text_label.find('-') >= 0:
                text_label = text_label.split('-')[0]
  
            # shows the selected items
            item_new_text_label = text_label + ' - selected index: ' + n
  
           # setting text to combo box
            self.setItemText(i, item_new_text_label)
  
    # flush    
    sys.stdout.flush()
###---------------------------Import der Datenbank---------------------------------###
### -------------------------------------------------------------------------------###
###---------------------------START------------------------------------------------###
### -------------------------------------------------------------------------------###
class Haupt_Fenster(QtWidgets.QMainWindow):
    def __init__(self):
        super(Haupt_Fenster, self).__init__()
        ui_file = Path(__file__).absolute().parent / "ui/HauptFenster_GUI.ui"
        uic.loadUi(ui_file,self) 
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        self.setAcceptDrops(True)
        self.tbl_INTAKA.verticalHeader().setVisible(False)
        self.tbl_INTDarsteller.verticalHeader().setVisible(False)
        self.tbl_INTHandlung.verticalHeader().setVisible(False)              
        self.tbl_INTAKA.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(2):
            self.tbl_INTDarsteller.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        self.tbl_INTDarsteller.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tbl_INTHandlung.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.Button_unsichtbar(True)
        ###---------------------------------Menu-Buttons-----------------------------------###
        ### -------------------------------------------------------------------------------### 
        self.actionINTERNET.triggered.connect(self.INTERNET_Ausgabe) 
        self.actionInfo.triggered.connect(self.Info_Ausgabe)        
        ###-------------------------auf Klicks reagieren--------------------------------------###
        self.DelBtn_DateiInfo.clicked.connect(self.InhaltLoeschen)         
        self.DateiBtn_Laden.clicked.connect(self.Info_Datei_Laden)
        self.CopyBtn_InfoDatei.clicked.connect(self.CopyClipboard_InfoDatei) 
        self.CopyBtn_InfoDaten.clicked.connect(self.CopyClipboard_InfoDaten)
        self.CopyBtn_InfoAKA.clicked.connect(self.CopyClipboard_InfoAKA) 
        self.CopyBtn_InfoDarsteller.clicked.connect(self.CopyClipboard_InfoDarsteller)
        self.nfoBtn_Maker.clicked.connect(self.nfoMaker)
        self.EditBtn_AKA.clicked.connect(self.Editieren)
        self.EditBtn_Darsteller.clicked.connect(self.Editieren)
        self.DateiBtn_nfoLaden.clicked.connect(self.nfoLoad)
        ### --------------------------- Check ComboBox ----------------------------------------###
        self.Sprach_CheckcBox = CheckableComboBox(self.DateiInfo)
        self.Sprach_CheckcBox.setGeometry(QtCore.QRect(170,445,261,20))
        self.Land_CheckcBox = CheckableComboBox(self.DateiInfo)
        self.Land_CheckcBox.setGeometry(QtCore.QRect(170,470,261,20))
        daten=[]
        with open(LAENDER_JSON_PATH, 'r') as f:
            daten=json.load(f)
        laender=daten["laender"];sprache=daten["sprachen"]
        for num,sprach_ger in enumerate(sprache.keys()):
            self.Sprach_CheckcBox.addItem(sprache[sprach_ger])
            item = self.Sprach_CheckcBox.model().item(num, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.Sprach_CheckcBox.setStyleSheet("QComboBox {color: rgb(0, 85, 0);background-color: white}")
        self.Sprach_CheckcBox.view().setStyleSheet("QComboBox, QComboBox QAbstractItemView {color: rgb(0, 85, 0);background-color: white}")  
        for num,land_ger in enumerate(laender.keys()):
            # adding item
            self.Land_CheckcBox.addItem(laender[land_ger])            
            item = self.Land_CheckcBox.model().item(num, 0)
            item.setCheckState(QtCore.Qt.Unchecked)                        
        self.Land_CheckcBox.setStyleSheet("QComboBox {color: rgb(0, 85, 0);background-color: white}")
        self.Land_CheckcBox.view().setStyleSheet("QComboBox QAbstractItemView {color: rgb(0, 85, 0);background-color: white}")             

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):	
        filenames = event.mimeData().text()
        filenames = filenames.split('\n')
        for filename in filenames:
            filename = filename.strip()
            if filename == '':
                continue
            if not filename.startswith('file:///'):
                print('bye')
                return
            filename = filename.replace('file:///', '')
            self.lbl_Datei.setText(filename)             
            self.DateiLaden(filename)

    # Info-Fenster Ausgabe und schließen
    def Info_Ausgabe(self):
        sender = self.sender()
        print(sender.objectName())                       
        #Fenster Anzeige
        self.InfoW=uic.loadUi(os.path.join(Path(__file__).absolute().parent / 'ui/Info.ui'))        
        self.InfoW.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint| 
                              QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)        
        self.InfoW.OKBtn.clicked.connect(self.Klick)
        self.InfoW.exec_()        
    def Klick(self):        
        self.InfoW.hide()
    ###---------------------------------Titel Auswahl-----------------------------------------###
    def zwei_auswahl(self,alt,neu,Titel):                           
        #Fenster Anzeige
        self.TitelAuswahlW=uic.loadUi(Path(__file__).absolute().parent / 'ui/Titel_Name_Auswahl.ui')        
        self.TitelAuswahlW.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint| 
                              QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)       
        self.TitelAuswahlW.show()
        self.ergebnis = ""
        self.TitelAuswahlW.gBox.setTitle("Welchen <b>"+Titel+"</b> behalten ?")
        self.TitelAuswahlW.rBtnName_alt.setText(alt)
        self.TitelAuswahlW.rBtnName_neu.setText(neu)
        self.TitelAuswahlW.OKBtnAuswahl.clicked.connect(self.auswahl)
        self.TitelAuswahlW.exec_()
        return self.ergebnis      
    def auswahl(self):        
        if self.TitelAuswahlW.rBtnName_neu.isChecked:
            self.ergebnis=self.TitelAuswahlW.rBtnName_neu.text()
        else:
            self.ergebnis=self.TitelAuswahlW.rBtnName_alt.text()            
        self.TitelAuswahlW.hide()
        return self.ergebnis        

    ###----------------------------- Tabelle Edit --------------------------------------------------###
    def Editieren(self):
        sender = self.sender()
        print(sender.objectName())
        if sender.objectName()=="EditBtn_AKA":
            self.EditierW=uic.loadUi(Path(__file__).absolute().parent / 'ui/AKAEdit.ui')
            SpaltenMax=3
            self.Fertig=self.EditierW.FertigBtn_AKAEdit
            self.Tadden=self.EditierW.TaddBtn_AKAEdit
            self.Zdel=self.EditierW.ZdelBtn_AKAEdit
            self.Zadd=self.EditierW.ZaddBtn_AKAEdit
            self.Edit=self.EditierW.tbl_AKAEdit
            self.DatenInfo=self.tblAKA
            Edit_Count=self.tblAKA.rowCount()
        else:
            self.EditierW=uic.loadUi(Path(__file__).absolute().parent / 'ui/DarstellerEdit.ui')
            SpaltenMax=4
            self.Fertig=self.EditierW.FertigBtn_DarstellerEdit            
            self.Zdel=self.EditierW.ZdelBtn_DarstellerEdit
            self.Zadd=self.EditierW.ZaddBtn_DarstellerEdit
            self.Edit=self.EditierW.tbl_DarstellerEdit
            self.DatenInfo=self.tblDarsteller
            Edit_Count=self.tblDarsteller.rowCount()
        #Fenster Anzeige                
        self.EditierW.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint| 
                              QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        self.Edit.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.Edit.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.Edit.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.Edit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.Edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)                                      
        self.EditierW.setMaximumHeight(165+Edit_Count*30) 
        self.Edit.setRowCount(Edit_Count)
        for spalte in range(SpaltenMax):           
            for zeile in range(Edit_Count):
                self.Edit.setItem(zeile, spalte,QtWidgets.QTableWidgetItem(self.DatenInfo.item(zeile,spalte).text()))                
        self.Fertig.clicked.connect(self.Editier_Fertig)
        if SpaltenMax==3:self.EditierW.TaddBtn_AKAEdit.clicked.connect(self.Titel_adden)
        self.Zdel.clicked.connect(self.Zeile_loeschen)
        self.Zadd.clicked.connect(self.Zeile_adden)
        self.EditierW.exec_()
    ###-----------------------------editierte Tabelle in Daten Tabelle wieder einfügen ----------------------------------------###
    def Editier_Fertig(self):
        try:            
            self.Edit=self.EditierW.tbl_AKAEdit
            SpaltenMax=3
            self.DatenInfo=self.tblAKA
        except:
            self.Edit=self.EditierW.tbl_DarstellerEdit
            SpaltenMax=4
            self.DatenInfo=self.tblDarsteller
        ZeileCount=self.Edit.rowCount()
        self.DatenInfo.setRowCount(ZeileCount)
        for spalte in range(SpaltenMax):                                  
            for zeile in range(ZeileCount):                
                self.DatenInfo.setItem(zeile, spalte,QtWidgets.QTableWidgetItem(self.Edit.item(zeile,spalte).text()))
                print("%s / %s" % (spalte,zeile))
        self.EditierW.hide()
    ###-----------------------------Titel in Tabelle einfügen -----------------------------------------------------------------###
    def Titel_adden(self):
        Titel=self.lblTitel.text();isvorhanden=0
        AKA_Count=self.EditierW.tbl_AKAEdit.rowCount()       
        for zeile in range(AKA_Count):            
            if self.EditierW.tbl_AKAEdit.item(zeile,0).text()== Titel:
                isvorhanden=1
                break
        if isvorhanden==0:
            AKA_Count+=1
            self.EditierW.tbl_AKAEdit.setRowCount(AKA_Count)
            self.EditierW.setMinimumHeight(165+AKA_Count*30)
            self.EditierW.resize(self.EditierW.width(),155+AKA_Count*32)
            self.EditierW.tbl_AKAEdit.setItem(AKA_Count-1,0,QtWidgets.QTableWidgetItem(Titel))
            self.EditierW.tbl_AKAEdit.setItem(AKA_Count-1,1,QtWidgets.QTableWidgetItem("Haupttitel"))
            self.EditierW.tbl_AKAEdit.setItem(AKA_Count-1,2,QtWidgets.QTableWidgetItem(""))
            self.EditierW.lblStatus.setStyleSheet("QLabel { color: green }")
            self.EditierW.lblStatus.setText("%s ist addet" % (Titel))
        else:
            self.EditierW.lblStatus.setStyleSheet("QLabel { color: red }")
            self.EditierW.lblStatus.setText('Titel schon in der Tabelle !')
    ###-----------------------------Zeile in Tabelle einfügen, um sie evtl zu editieren ----------------------------------------###
    def Zeile_adden(self):
        try:            
            self.Edit=self.EditierW.tbl_AKAEdit
            SpaltenMax=3
        except:
            self.Edit=self.EditierW.tbl_DarstellerEdit
            SpaltenMax=4
        isvorhanden=0
        AKA_Count=self.Edit.rowCount()               
        for zeile in range(AKA_Count):            
            if self.Edit.item(zeile,0).text()== "":
                isvorhanden=1
                break
        if isvorhanden==0:
            AKA_Count+=1
            self.Edit.setRowCount(AKA_Count)
            self.EditierW.setMinimumHeight(165+AKA_Count*30)
            self.EditierW.resize(self.EditierW.width(),165+AKA_Count*30)
            for spalte in range(SpaltenMax):
                self.Edit.setItem(AKA_Count-1,spalte,QtWidgets.QTableWidgetItem(""))
            self.EditierW.lblStatus.setStyleSheet("QLabel { color: green }")
            self.EditierW.lblStatus.setText("Eine Zeile ist addet")
        else:
            self.EditierW.lblStatus.setStyleSheet("QLabel { color: red }")
            self.EditierW.lblStatus.setText('Eine leere zeile ist schon in der Tabelle !')
    ###----------------------------- Zeile löschen -------------------------------------------------------------------------------###
    def Zeile_loeschen(self):
        try:            
            self.Edit=self.EditierW.tbl_AKAEdit
        except:
            self.Edit=self.EditierW.tbl_DarstellerEdit
        select=self.Edit.selectedIndexes()
        AKA_Count=self.Edit.rowCount()
        if AKA_Count==0:
            self.EditierW.lblStatus.setStyleSheet("QLabel { color: red }")
            self.EditierW.lblStatus.setText('Es sind keine Zeilen in der Tabelle vorhanden !')
        elif len(select)==0:
            self.EditierW.lblStatus.setStyleSheet("QLabel { color: red }")
            self.EditierW.lblStatus.setText('Du haste keine Zeile markiert !')
        else:            
            for sel in select:
                AKA_Count-=1
                zeile=sel.row()
                Titel=self.Edit.item(zeile,0).text()
                self.Edit.removeRow(zeile)   
                self.EditierW.lblStatus.setStyleSheet("QLabel { color: green }")
                self.EditierW.lblStatus.setText("Zeile %s mit dem Titel: ""%s"" ist gelöscht" % (zeile+1,Titel))
                self.EditierW.setMinimumHeight(165+AKA_Count*30)
                self.EditierW.resize(self.EditierW.width(),165+AKA_Count*30)
                QtWidgets.QApplication.processEvents()
                time.sleep(4)

    ###-----------------------------Darsteller Edit -------------------------------------------###  
    def InhaltLoeschen(self):
        self.lbl_Datei.setText("")
        self.lblTitel.setText("")
        self.lblLabel.setText("Regie             =\nLabel             =\nSerie             =\nErscheinungsdatum = ")
        self.lblnfoDaten.setText("Format		  =\nResize		  = \nLaufzeit          = ")   
        self.tblAKA.setRowCount(0)
        self.lblLinks.setText("")
        self.tblDarsteller.setRowCount(0)
        self.lblHandlung.setText("")
        self.Button_unsichtbar(True)
    def clear_INTFenster(self):
        self.lnEdit_INTLinkEingabe.setText("")
        self.lbl_INTName.setText("")        
        self.lbl_INTRegie.setText("")
        self.lbl_INTSprache.setText("")
        self.lbl_INTDatum.setText("")
        self.lbl_INTLabel.setText("")
        self.lbl_INTSerie.setText("")
        self.lbl_INTLand.setText("")
        self.tbl_INTAKA.setRowCount(0)
        self.tbl_INTDarsteller.setRowCount(0)
        self.tbl_INTHandlung.setRowCount(0)
    def MsgBox(self,Daten,art):
        mBox = QtWidgets.QMessageBox()
        if art=='w':                   
            QtWidgets.QMessageBox.warning(mBox, 'Fataler Fehler',
                """<font color='black'>
                <style><background-color='yellow'>
                <h1 text-align: center></style>
                <h1>Fataler Fehler</h1>
                <img src='./images/sign-error-icon.png' alt='ERROR'></img>
                <p><font-size: 20px><b>{0}</b></p></body>""".format(Daten))
        if art=='q':  
            reply=QtWidgets.QMessageBox.question(mBox, 'Fataler Fehler',
                """<h1>Bist du Sicher ?</h1>""",QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
        if art=="i":
            QtWidgets.QMessageBox.information(mBox, 'Bitte warten !',
                """<font color='black'>
                <style><background-color='green'>
                <h1 text-align: center></style>
                <h1>Bitte warte bis die Seite geladen ist</h1>
                <img src='./images/sanduhr.png' alt='ERROR'></img>
                <p><font-size: 20px><b>{0}</b></p></body>""".format(Daten)) 
        return reply

    def Info_Datei(self,art):            
        dialog = QtWidgets.QFileDialog(self,"Ordner öffnen")
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        dialog.setDirectory("D:\\")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if art=="Video":dialog.setNameFilter("Movie Daten (*.mp4 *.avi *wmv)")
        if art=="nfo":dialog.setNameFilter("nfo Daten (*.txt)")        
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            return dialog.selectedFiles()[0]           
            

    def DateiLaden(self,filename):
        if filename is not None:                    
            self.lbl_Datei.setText(filename) 
            filename=filename.replace("/","\\")           
            TheShell = win32com.client.gencache.EnsureDispatch('Shell.Application',0)
            AFolder = TheShell.NameSpace(os.path.dirname(filename))
            AFile = AFolder.ParseName(os.path.basename(filename))                             
            Groesse=re.sub(r"\s+", "",AFolder.GetDetailsOf(AFile,1))
            file=AFolder.GetDetailsOf(AFile,165)[0:-4] 
            striche=("-"*len(file))
            ms_codec=AFolder.GetDetailsOf(AFile,311)
            codecs={"{34363248-0000-0010-8000-00AA00389B71}":"H.264",
                    "{5634504D-0000-0010-8000-00AA00389B71}":"MPEG-4 Part 2",
                    "{3253344D-0000-0010-8000-00AA00389B71}":"MPEG-4 Advanced Simple Profile",
                    "{32564D57-0000-0010-8000-00AA00389B71}":"Windows Media Video 8",
                    "{3334504D-0000-0010-8000-00AA00389B71}":"Microsoft MPEG-4 version 3",    
                    }
            CodecVersion=codecs.get(ms_codec)
            if CodecVersion==None:
                Breite="000";Hoehe="000";Bitrate="0";Dauer="00:00:00";Brate="00.00";Format="Unbekannt";CodecVersion="Unbekannt"
            else:     
                Breite=AFolder.GetDetailsOf(AFile,316)
                Hoehe=AFolder.GetDetailsOf(AFile,314)
                Bitrate=str(AFolder.GetDetailsOf(AFile,313).replace('kBit/s','').replace("\u200e","").strip())
                Dauer=AFolder.GetDetailsOf(AFile,27)
                Brate=str(AFolder.GetDetailsOf(AFile,315).replace(' Bilder/Sekunde','').replace("\u200e",""))        
                if int(Hoehe)>=720 and int(Hoehe)<1080:
                    Format="HD 720p"
                elif int(Hoehe)<720:
                    Format="DVD"
                else: Format="FULLHD 1080p"  
            inhalt=("Format            = "+Format+
                    " \nResize		  = "+Groesse+" - "+Bitrate+"kb/s ("+str(Breite)+" x "+str(Hoehe)+" / "+Brate+"f) "+CodecVersion+
                    "\nLaufzeit          = "+Dauer)         
            self.lblTitel.setText(file+"\n"+striche)
            self.lblnfoDaten.setText(inhalt)         
            pyperclip.copy(inhalt)
        

    ###----------------- zurück zum Hauptmenu per Button --------------------------------###
    ###----------------------------------------------------------------------------------###
    def Zurueck(self):
        ###-------------------------Fenster Anzeigen.-----------------------------------------###
        ### ----------------------------------------------------------------------------------###
        self.stackedWidget.setCurrentIndex(0)
        self.Button_unsichtbar(True)

    def INTERNET_Ausgabe(self):
        ###-------------------------Fenster Anzeigen.-----------------------------------------###
        ### ----------------------------------------------------------------------------------###
        self.stackedWidget.setCurrentWidget(self.INTERNET)
        self.CopyBtn_nfo_INT.setHidden(True) 
        ###-------------------------auf Klicks reagieren--------------------------------------###
        self.ExitBtn_INT.clicked.connect(self.Zurueck)
        self.SuchBtnURL_INT.clicked.connect(self.Internet_Laden)
        self.CopyBtn_nfo_INT.clicked.connect(self.Copynfo)
        
    def Button_unsichtbar(self,Status):
        if self.lblTitel.text()=="":Status=True
        self.CopyBtn_InfoDatei.setHidden(Status)
        self.EditBtn_AKA.setHidden(Status)
        self.CopyBtn_InfoAKA.setHidden(Status)
        self.CopyBtn_InfoDaten.setHidden(Status)
        self.CopyBtn_InfoDarsteller.setHidden(Status)
        self.EditBtn_Darsteller.setHidden(Status)
        self.nfoBtn_Maker.setHidden(Status)

    def Internet_Laden(self):
        ink=""
        self.SuchBtnURL_INT.setEnabled(False)
        self.ExitBtn_INT.setEnabled(False)
        url=self.lnEdit_INTLinkEingabe.text()
        if "iafd.com" in url[:20]:
            ink = QtGui.QPixmap(str(Path(__file__).absolute().parent / "images/IAFD.png"))            
            WebSide="IAFD"
        if "imdb.com" in url[:20]:
            ink = QtGui.QPixmap(str(Path(__file__).absolute().parent / "images/IMDb.png"))
            WebSide="IMDb"        
        self.lbl_INTLogo.setPixmap(ink)
        QtWidgets.QApplication.processEvents()
        Options.headless = True 
        firefox_profile = FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        driver = Firefox(options=Options,firefox_profile=firefox_profile,executable_path=GECKO)               
        driver.get(url)
        Titel=Scraping.Titel_Scraping(WebSide,driver)
        if Titel[len(Titel):-1].isdigit():
            Serie=Titel[:Titel[:-1].rfind(" ")]  
        self.lbl_INTName.setText(Titel)
        ### --------------------------------- Regie                     ------------------------------------- ###
        Regie=Scraping.Regie_Scraping(WebSide,driver)
        self.lbl_INTRegie.setText(Regie)
        ### --------------------------------- Land                      ------------------------------------- ###
        Land=Scraping.Land_Scraping(WebSide,driver) 
        self.lbl_INTLand.setText(Land)
        ### --------------------------------- Label und Distributor     ------------------------------------- ###             
        Distributor=Scraping.Label_Scraping(WebSide,driver)
        self.lbl_INTLabel.setText(Distributor)
        ### --------------------------------- Release-Datum -------------------------------------------------- ### 
        ReleaseDate=Scraping.ReleaseDatum_Scraping(WebSide,driver)
        with open(Path(__file__).absolute().parent / "JSON/url.json", 'r') as f:
            infos=json.load(f)  
        self.lbl_INTDatum.setText(infos["Datum"])
        ### --------------------------------- AKA in eine Tabelle laden -------------------------------------- ###        
        ###--------------------------------------------------------------------------------------------------- ### 
        if "imdb.com" in url[:20]:
            driver.get(infos["akaLink"])            
        Also_Known_As=Scraping.AKA_Scraping(WebSide,driver)
        if Also_Known_As=="":self.statusBar.showMessage("AKA: Keine Daten !",2000)                        
        self.tbl_INTAKA.setRowCount(len(Also_Known_As))
        for spalte in range(len(Also_Known_As)):
            for reihe,AKA_single in enumerate(Also_Known_As[spalte]):            
                self.tbl_INTAKA.setItem(spalte,reihe, QtWidgets.QTableWidgetItem(AKA_single))
        ### --------------------------------- Szenen in eine Tabelle packen ----------------------------------- ###
        Szenen=Scraping.Szenen_Scraping(WebSide,driver)
        self.tbl_INTHandlung.setRowCount(len(Szenen))
        for spalte in range(len(Szenen)):
            for reihe,Szene in enumerate(Szenen[spalte]):
                self.tbl_INTHandlung.setItem(spalte, reihe, QtWidgets.QTableWidgetItem(Szene)) 
        ### --------------------------------- Darsteller in eine Tabelle packen-------------------------------- ###
        if "imdb.com" in url[:20] and infos.get("DarstellerLink")!="":
            driver.get(infos["DarstellerLink"])    
        Performer=Scraping.Darsteller_Scraping(WebSide,driver)                        
        self.tbl_INTDarsteller.setRowCount(len(Performer))
        for spalte in range(len(Performer)):
            for reihe,Performer_single in enumerate(Performer[spalte]):            
                self.tbl_INTDarsteller.setItem(spalte,reihe, QtWidgets.QTableWidgetItem(Performer_single))        
        ### --------------------------------------------------------------------------------------------------- ###    
        driver.quit()
        self.CopyBtn_nfo_INT.setHidden(False)
        self.SuchBtnURL_INT.setEnabled(True)
        self.ExitBtn_INT.setEnabled(True)

    def Copynfo(self):
        ### -------------------------------Titel ------------------------------------------------------ ### 
        print(self.lblLinks.text().find(self.lnEdit_INTLinkEingabe.text()))       
        if self.lblLinks.text().find(self.lnEdit_INTLinkEingabe.text())>17:
            self.stackedWidget.setCurrentIndex(0)
            self.clear_INTFenster()        
            self.Button_unsichtbar(False)            
        alt=self.lblTitel.text()
        neu=self.lbl_INTName.text()
        ergebnis=neu;serie=""
        if alt!=neu and alt!="":          
            ergebnis=self.zwei_auswahl(alt,neu,"Titel")                         
        self.lblTitel.setText(ergebnis)     
        ### ------------------------------- Anhand des Titel prüfen ob Serie -------------------------- ###        
        if ergebnis[len(ergebnis):-1].isdigit():
            serie=ergebnis=[ergebnis[:-1].rfind(" ")]
        ### ------------------------------- Datum, Label und Co --------------------------------------- ###        
        if self.lblRegie.text()=="":
            self.lblRegie.setText(self.lbl_INTRegie.text())
        else:
            alt=self.lblRegie.text()
            neu=self.lbl_INTRegie.text();ergebnis=neu
            if alt!=neu and alt!="":          
                ergebnis=self.zwei_auswahl(alt,neu,"Regiename")                            
        self.lblTitel.setText(ergebnis) 
        if self.lblLabel.text()=="":
            self.lblLabel.setText(self.lbl_INTLabel.text())
        else:
            alt=self.lblLabel.text()
            neu=self.lbl_INTLabel.text();ergebnis=neu
            if alt!=neu and alt!="":          
                ergebnis=self.zwei_auswahl(alt,neu,"Studioname")                       
        self.lblTitel.setText(ergebnis)
        if self.lblDatum.text()=="":
            self.lblDatum.setText(self.lbl_INTDatum.text())
        else:
            alt=self.lblDatum.text()
            neu=self.lbl_INTDatum.text();ergebnis=neu
            if alt!=neu and alt!="":          
                ergebnis=self.zwei_auswahl(alt,neu,"Datum")                   
        self.lblTitel.setText(ergebnis)
        if self.lblSerie.text()=="":
            self.lblSerie.setText(serie)
        for num in range(len(self.Land_CheckcBox)):            
            if self.Land_CheckcBox.model().item(num, 0).text()==self.lbl_INTLand.text():
                item = self.Land_CheckcBox.model().item(num, 0)
                item.setCheckState(QtCore.Qt.Checked)                
          ### ------------------------------- Tabelle AKA --------------------------------------------- ###                    
        tblAKA={};tblINTAKA={}
        for reihe in range(self.tblAKA.rowCount()):
            tblAKA.update({self.tblAKA.item(reihe, 0).text():(self.tblAKA.item(reihe, 1).text(),self.tblAKA.item(reihe, 2).text())})
        for reihe in range(self.tbl_INTAKA.rowCount()):            
            tblINTAKA.update({self.tbl_INTAKA.item(reihe, 0).text():(self.tbl_INTAKA.item(reihe, 1).text(),self.tbl_INTAKA.item(reihe, 2).text())})
        for name, art_land in tblINTAKA.items():
            if name not in tblAKA:
                neue_Zeile=self.tblAKA.rowCount()+1
                self.tblAKA.setRowCount(neue_Zeile)
                self.tblAKA.setItem(neue_Zeile-1, 0,QtWidgets.QTableWidgetItem(name))                               
                self.tblAKA.setItem(neue_Zeile-1, 1,QtWidgets.QTableWidgetItem(art_land[0]))
                self.tblAKA.setItem(neue_Zeile-1, 2,QtWidgets.QTableWidgetItem(art_land[1]))                
        ### ------------------------------- Tabelle Darsteller ---------------------------------------- ###                
        tblDarstel={};tblINTDarstel={}
        for reihe in range(self.tblDarsteller.rowCount()):
            tblDarstel.update({self.tblDarsteller.item(reihe, 0).text():(self.tblDarsteller.item(reihe, 1).text(),self.tblDarsteller.item(reihe, 2).text(),self.tblDarsteller.item(reihe, 3).text())})
        for reihe in range(self.tbl_INTDarsteller.rowCount() ):
            tblINTDarstel.update({self.tbl_INTDarsteller.item(reihe, 0).text():(self.tbl_INTDarsteller.item(reihe, 1).text(),self.tbl_INTDarsteller.item(reihe, 2).text(),self.tbl_INTDarsteller.item(reihe, 3).text())})
        for name, rolle_alias_art in tblINTDarstel.items():
            if name not in tblDarstel:                
                neue_Zeile=self.tblDarsteller.rowCount()+1
                self.tblDarsteller.setRowCount(neue_Zeile)
                self.tblDarsteller.setItem(neue_Zeile-1, 0,QtWidgets.QTableWidgetItem(name))                
                self.tblDarsteller.setItem(neue_Zeile-1, 1,QtWidgets.QTableWidgetItem(rolle_alias_art[0]))
                self.tblDarsteller.setItem(neue_Zeile-1, 2,QtWidgets.QTableWidgetItem(rolle_alias_art[1]))
                self.tblDarsteller.setItem(neue_Zeile-1, 3,QtWidgets.QTableWidgetItem(rolle_alias_art[2]))                        
        ### ------------------------------- Label Handlung --------------------------------------------- ###
        Inhalt=""
        if self.tbl_INTHandlung.rowCount()>0:
            for reihe in range(self.tbl_INTHandlung.rowCount()):
                Inhalt+="Szene "+str(reihe+1)+": "+self.tbl_INTHandlung.item(reihe, 3).text()+"\n"
            self.lblHandlung.setText(Inhalt)
        ### ------------------------------- Links ------------------------------------------------------ ###        
        self.lblLinks.setText(self.lblLinks.text()+self.lnEdit_INTLinkEingabe.text()+"\n")
        ### ------------------------------- Anzeige Titel-Fenster und Inhalt löschen ------------------- ###        
        self.stackedWidget.setCurrentIndex(0)
        self.clear_INTFenster()        
        self.Button_unsichtbar(False)

    def nfoMaker(self):
        ###------------------------ von Tabelle Darsteller in String umwandeln --------------------------###
        Darsteller=self.Tabelle_Darsteller()
        Auch_bekannt_Als=self.Tabelle_AKA()
        Label="Regie             = "+self.lblRegie.text()+"\nLabel             = "+self.lblLabel.text()+"\nSerie             = "+self.lblSerie.text()+"\nErscheinungsdatum = "+self.lblDatum.text()
        ###------------------------- nfo speichern und ins Movie Ordner schieben ------------------------###
        with open(Path(__file__).absolute().parent /'nfo.txt', 'w+', encoding='utf-8') as AllItems:
            Inhalt = self.lblTitel.text()+"\n"+"-"*len(self.lblTitel.text())+"\nAKA\n"+Auch_bekannt_Als+"\nLinks:\n"+self.lblLinks.text()+"\n\n"+Label+"\n"+self.lblnfoDaten.text()+"\nSprache           =\nLand              =\n\n"+Darsteller+"\nHandlung:\n"+self.lblHandlung.text()
            #Inhalt.encode("ascii", "ignore")
            AllItems.write(Inhalt)
        source=Path(__file__).absolute().parent / 'nfo.txt'
        destination=os.path.join(os.path.dirname(self.lbl_Datei.text()),"nfo.txt")                   
        shutil.move(source, destination)
        os.system("start notepad.exe "+destination)
    
    def nfoLoad(self):
        destination=self.Info_Datei("nfo")
        try: 
            with open(destination,'r') as file:
                nfo = file.read().split("\n")
            Titel=nfo[0];akas=[]
            print("Titel: %s\n" % Titel)
            if nfo[2]=="AKA":
                for index in range(2,len(nfo)):
                    if nfo[index]=="Links:":                                        
                        for i in range(3,index):                                                
                            if nfo[i].strip()!="":akas.append(nfo[i].strip())
                print("AKAs: %s\n" % akas)
        except:
            print("keine Datei gefunden")

    def Info_Datei_Laden(self):
        self.DateiLaden(self.Info_Datei("Video"))

    def Tabelle_AKA(self):
        AlsoKnownAs="";Art="";Land_AKA=""
        for reihe in range(self.tblAKA.rowCount()):
            AKA_Titel =self.tblAKA.item(reihe, 0).text()            
            if self.tblAKA.item(reihe, 1).text()!="":
                Art="Titel in "+self.tblAKA.item(reihe, 1).text()            
            if self.tblAKA.item(reihe, 2).text()!="":
                Land_AKA=self.tblAKA.item(reihe, 2).text()+": "   
            AlsoKnownAs+=Art+Land_AKA+AKA_Titel+"\n" 
        return AlsoKnownAs

    def Tabelle_Darsteller(self):        
        Zelle=[0,0,0,0];a=""        
        for spalte in range(4):
            for reihe in range(self.tblDarsteller.rowCount()):                                            
                if len(self.tblDarsteller.item(reihe, spalte).text())>Zelle[spalte]:
                    Zelle[spalte]=len(self.tblDarsteller.item(reihe, spalte).text()) 
        a+="╔"+"═"*(Zelle[0]+Zelle[1]+Zelle[2]+Zelle[3]+11)+"╗\n"
        a+="║ Darsteller:"+" "*(Zelle[0]+Zelle[1]+Zelle[2]+Zelle[3]-2)+" ║\n"
        z1="╦";z2=z1;za1=" ║ ";za2=za1;zb1="╩";zb2=zb1
        if Zelle[1]==0:z1="═";za1="  ";zb1="═"        
        if Zelle[2]==0:z2="═";za2="   ";zb2="═"        
        a+="╠"+"═"*(Zelle[0]+2)+"╦"+"═"*(Zelle[1]+2)+z1+"═"*(Zelle[2]+2)+z2+"═"*(Zelle[3]+2)+"╣\n"
        for reihe in range(self.tblDarsteller.rowCount()):
            name=self.tblDarsteller.item(reihe, 0).text()
            rollenname=self.tblDarsteller.item(reihe, 1).text()
            Alias=self.tblDarsteller.item(reihe, 2).text()
            Art=self.tblDarsteller.item(reihe, 3).text()
            a+="║ "+name+" "*(Zelle[0]-len(name))+" ║ "+rollenname+" "*(Zelle[1]-len(rollenname))+za1+Alias+" "*(Zelle[2]-len(Alias))+za2+Art+" "*(Zelle[3]-len(Art))+"  ║\n"            
        a+="╚"+"═"*(Zelle[0]+2)+"╩"+"═"*(Zelle[1]+2)+zb1+"═"*(Zelle[2]+2)+zb2+"═"*(Zelle[3]+2)+"╝\n"
        return a

    def CopyClipboard_InfoDatei(self):
        pyperclip.copy(self.lblTiteltext())
    def CopyClipboard_InfoDaten(self):
        pyperclip.copy(self.lblnfoDaten.text())
    def CopyClipboard_InfoAKA(self):
        Auch_bekannt_Als=self.Tabelle_AKA()
        pyperclip.copy(Auch_bekannt_Als+"\nLinks:\n"+self.lblLinks.text()+"\n\n"+self.lblLabel.text())
    def CopyClipboard_InfoDarsteller(self):
        a=self.Tabelle_Darsteller()
        pyperclip.copy("\n"+a+"\nHandlung:\n"+self.lblHandlung.text())



# Abschluss
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Haupt_Fenster() 
    MainWindow.show()   
    sys.exit(app.exec_())