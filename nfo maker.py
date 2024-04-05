from PyQt6 import uic
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtWidgets import QMainWindow, QComboBox, QHeaderView, QHeaderView, QSizePolicy, QAbstractScrollArea, QTableWidgetItem,\
    QApplication, QMessageBox, QFileDialog, QDialog
from PyQt6.QtGui import QStandardItemModel, QPixmap

import sys
import re
import win32com.client
import shutil
import time
import json

import pyperclip
from pathlib import Path
import os

from utils.scraping import Scraping
from utils.message_show import StatusBar, status_fehler_ausgabe

LAENDER_JSON_PATH = Path(__file__).absolute().parent / "JSON/laender.json"

class CheckableComboBox(QComboBox):
    def __init__(self,parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QStandardItemModel(self))  
    
    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked) 
        self.check_items()  
    
    def item_checked(self, index):        
        item = self.model().item(index, 0)        
        return item.checkState() == Qt.CheckState.Checked  
    
    def check_items(self):        
        checkedItems = []  
        for i in range(self.count()):
            if self.item_checked(i):
                checkedItems.append(i) 
        self.update_labels(checkedItems)  
    
    def update_labels(self, item_list):  
        n = ''
        count = 0          
        for i in item_list: 
            if count == 0:
                n += ' % s' % i            
            else:
                n += ', % s' % i  
            count += 1
        for i in range(self.count()):
            text_label = self.model().item(i, 0).text()
            if text_label.find('-') >= 0:
                text_label = text_label.split('-')[0]
            item_new_text_label = text_label + ' - selected index: ' + n
            self.setItemText(i, item_new_text_label) 
    sys.stdout.flush()

###---------------------------START------------------------------------------------###
### -------------------------------------------------------------------------------###
class Haupt_Fenster(QMainWindow):
    def __init__(self):
        super(Haupt_Fenster, self).__init__()
        ui_file = Path(__file__).absolute().parent / "ui/HauptFenster_GUI.ui"
        uic.loadUi(ui_file, self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setAcceptDrops(True)
        self.tbl_INTAKA.verticalHeader().setVisible(False)
        self.tbl_INTDarsteller.verticalHeader().setVisible(False)
        self.tbl_INTHandlung.verticalHeader().setVisible(False)              
        self.tbl_INTAKA.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(2):
            self.tbl_INTDarsteller.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_INTDarsteller.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tbl_INTHandlung.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.set_button_visible(False)
        ###---------------------------------Menu-Buttons-----------------------------------###
        ### -------------------------------------------------------------------------------### 
        self.actionINTERNET.triggered.connect(self.internet_output) 
        self.actionInfo.triggered.connect(self.Info_Ausgabe)        
        ###-------------------------auf Klicks reagieren--------------------------------------###
        self.Btn_get_url_infos.clicked.connect(self.get_url_infos)
        self.DelBtn_DateiInfo.clicked.connect(self.InhaltLoeschen)         
        self.Btn_load_file.clicked.connect(self.get_file_datas_Laden)
        self.CopyBtn_InfoDatei.clicked.connect(self.CopyClipboard_InfoDatei) 
        self.Btn_copy_infodatas.clicked.connect(self.CopyClipboard_InfoDaten)
        self.CopyBtn_InfoAKA.clicked.connect(self.CopyClipboard_InfoAKA) 
        self.CopyBtn_InfoDarsteller.clicked.connect(self.CopyClipboard_InfoDarsteller)
        self.Btn_nfo_maker.clicked.connect(self.nfo_maker)
        self.EditBtn_AKA.clicked.connect(self.Editieren)
        self.EditBtn_Darsteller.clicked.connect(self.Editieren)
        self.Btn_load_nfo_file.clicked.connect(self.nfo_file_load)
        ### --------------------------- Check ComboBox ----------------------------------------###
        self.Sprach_CheckcBox = CheckableComboBox(self.DateiInfo)
        self.Sprach_CheckcBox.setGeometry(QRect(170,515,261,20))
        self.Land_CheckcBox = CheckableComboBox(self.DateiInfo)
        self.Land_CheckcBox.setGeometry(QRect(170,540,261,20))
        daten=[]
        with open(LAENDER_JSON_PATH, 'r') as f:
            daten=json.load(f)
        laender = daten["laender"]
        sprache = daten["sprachen"]
        for num,sprach_ger in enumerate(sprache.keys()):
            self.Sprach_CheckcBox.addItem(sprache[sprach_ger])
            item = self.Sprach_CheckcBox.model().item(num, 0)
            item.setCheckState(Qt.CheckState.Unchecked)
        self.Sprach_CheckcBox.setStyleSheet("QComboBox {color: rgb(0, 85, 0);background-color: white}")
        self.Sprach_CheckcBox.view().setStyleSheet("QComboBox, QComboBox QAbstractItemView {color: rgb(0, 85, 0);background-color: white}")  
        for num,land_ger in enumerate(laender.keys()):
            # adding item
            self.Land_CheckcBox.addItem(laender[land_ger])            
            item = self.Land_CheckcBox.model().item(num, 0)
            item.setCheckState(Qt.CheckState.Unchecked)                        
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
            self.lbl_movie_file.setText(filename)             
            self.files_load(filename)

    # Info-Fenster Ausgabe und schließen
    def Info_Ausgabe(self):
        sender = self.sender()        
        self.InfoW=uic.loadUi(Path(__file__).absolute().parent / 'ui/Info.ui')        
        self.InfoW.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint| 
                              Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)        
        self.InfoW.OKBtn.clicked.connect(self.InfoW.hide)
        self.InfoW.exec()      
    
    ###---------------------------------Titel Auswahl-----------------------------------------###
    def zwei_auswahl(self,alt,neu,Titel): 
        self.TitelAuswahlW=uic.loadUi(Path(__file__).absolute().parent / 'ui/Titel_Name_Auswahl.ui')        
        self.TitelAuswahlW.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint| 
                              Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)       
        self.TitelAuswahlW.show()
        self.ergebnis = ""
        self.TitelAuswahlW.gBox.setTitle("Welchen <b>"+Titel+"</b> behalten ?")
        self.TitelAuswahlW.rBtnName_alt.setText(alt)
        self.TitelAuswahlW.rBtnName_neu.setText(neu)
        self.TitelAuswahlW.OKBtnAuswahl.clicked.connect(self.auswahl)
        self.TitelAuswahlW.exec()
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
        self.EditierW.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint| 
                              Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.Edit.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.Edit.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.Edit.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.Edit.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.Edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)                                      
        self.EditierW.setMaximumHeight(165+Edit_Count*30) 
        self.Edit.setRowCount(Edit_Count)
        for spalte in range(SpaltenMax):           
            for zeile in range(Edit_Count):
                self.Edit.setItem(zeile, spalte,QTableWidgetItem(self.DatenInfo.item(zeile,spalte).text()))                
        self.Fertig.clicked.connect(self.Editier_Fertig)
        if SpaltenMax==3:self.EditierW.TaddBtn_AKAEdit.clicked.connect(self.Titel_adden)
        self.Zdel.clicked.connect(self.Zeile_loeschen)
        self.Zadd.clicked.connect(self.Zeile_adden)
        self.EditierW.exec()
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
                self.DatenInfo.setItem(zeile, spalte,QTableWidgetItem(self.Edit.item(zeile,spalte).text()))
                print("%s / %s" % (spalte,zeile))
        self.EditierW.hide()
    ###-----------------------------Titel in Tabelle einfügen -----------------------------------------------------------------###
    def Titel_adden(self):
        Titel=self.lbl_movie_title.text();isvorhanden=0
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
            self.EditierW.tbl_AKAEdit.setItem(AKA_Count-1,0,QTableWidgetItem(Titel))
            self.EditierW.tbl_AKAEdit.setItem(AKA_Count-1,1,QTableWidgetItem("Haupttitel"))
            self.EditierW.tbl_AKAEdit.setItem(AKA_Count-1,2,QTableWidgetItem(""))
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
                self.Edit.setItem(AKA_Count-1,spalte,QTableWidgetItem(""))
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
                self.EditierW.lblStatus.setText(f"Zeile {zeile+1} mit dem Titel: {Titel} ist gelöscht")
                self.EditierW.setMinimumHeight(165+AKA_Count*30)
                self.EditierW.resize(self.EditierW.width(),165+AKA_Count*30)
                QApplication.processEvents()
                time.sleep(4)

    ###-----------------------------Darsteller Edit -------------------------------------------###  
    def InhaltLoeschen(self):
        self.lbl_movie_file.setText("")
        self.lbl_movie_title.setText("")
        self.lbl_movie_studio.setText(f"{'Regie':18} =\n" \
                              f"{'Studio':18}=\n" \
                              f"{'Serie':18}=\n" \
                              f"{'Erscheinungsdatum':18}= " )
        self.lblnfoDaten.setText(f"{'Format':18}=\n" \
                                 f"{'Resize':18}= \n" \
                                 f"{'Laufzeit':18}= "   )   
        self.tblAKA.setRowCount(0)
        self.lblLinks.setText("")
        self.tblDarsteller.setRowCount(0)
        self.lblHandlung.setText("")
        self.set_button_visible(False)

    def clear_website_window(self):
        self.lnEdit_scrape_url.setText("")
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
        mBox = QMessageBox()
        if art=='w':                   
            QMessageBox.warning(mBox, 'Fataler Fehler',
                """<font color='black'>
                <style><background-color='yellow'>
                <h1 text-align: center></style>
                <h1>Fataler Fehler</h1>
                <img src='./images/sign-error-icon.png' alt='ERROR'></img>
                <p><font-size: 20px><b>{0}</b></p></body>""".format(Daten))
        if art=='q':  
            reply=QMessageBox.question(mBox, 'Fataler Fehler',
                """<h1>Bist du Sicher ?</h1>""",QMessageBox.Yes,QMessageBox.No)
        if art=="i":
            QMessageBox.information(mBox, 'Bitte warten !',
                """<font color='black'>
                <style><background-color='green'>
                <h1 text-align: center></style>
                <h1>Bitte warte bis die Seite geladen ist</h1>
                <img src='./images/sanduhr.png' alt='ERROR'></img>
                <p><font-size: 20px><b>{0}</b></p></body>""".format(Daten)) 
        return reply

    def get_file_datas(self, art):            
        dialog = QFileDialog(self,"Ordner öffnen")        
        dialog.setDirectory("D:\\")        
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if art == "Video":
            dialog.setNameFilter("Movie Daten (*.mp4 *.avi *wmv)")
        if art == "nfo":
            dialog.setNameFilter("nfo Daten (*.txt)")        
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if dialog.exec() == QDialog.DialogCode.Accepted:            
            return dialog.selectedFiles()[0] 

    def get_file_details(self, filename):
        folder_path = Path(filename).parent
        file_name = Path(filename).name
        
        windows_COM = win32com.client.gencache.EnsureDispatch('Shell.Application', 0)
        win_folder = windows_COM.NameSpace(str(folder_path))
        win_file = win_folder.ParseName(file_name)
        return win_folder, win_file

    def get_video_codec(self, ms_codec):
        codecs = {
            "{34363248-0000-0010-8000-00AA00389B71}": "H.264",
            "{5634504D-0000-0010-8000-00AA00389B71}": "MPEG-4 Part 2",
            "{3253344D-0000-0010-8000-00AA00389B71}": "MPEG-4 Advanced Simple Profile",
            "{32564D57-0000-0010-8000-00AA00389B71}": "Windows Media Video 8",
            "{3334504D-0000-0010-8000-00AA00389B71}": "Microsoft MPEG-4 version 3",
        }
        return codecs.get(ms_codec, "Unbekannt")

    def get_video_properties(self, win_folder, win_file):
        video_breite = win_folder.GetDetailsOf(win_file, 316)
        video_hoehe = win_folder.GetDetailsOf(win_file, 314)
        bitrate = win_folder.GetDetailsOf(win_file, 313).replace('kBit/s', '').replace("\u200e", "").strip()
        runtime = win_folder.GetDetailsOf(win_file, 27)
        frame_rate = win_folder.GetDetailsOf(win_file, 315).replace(' Bilder/Sekunde', '').replace("\u200e", "")
        return video_breite, video_hoehe, bitrate, runtime, frame_rate

    def get_format_resolution(self, height):
        height = int(height) if height else 0   
        if height < 720 and height >= 300:
            return "DVD"
        elif height < 1080:
            return "HD 720p"
        else:
            return "FULLHD 1080p"

    def build_content_format(self, file_size, video_breite, video_hoehe, bitrate, frame_rate, codec_version):        
        video_format = self.get_format_resolution(video_hoehe)
        content = (
            f"{'Format':18}= {video_format}\n"
            f"{'Resize':18}= {file_size} - {bitrate}kb/s ({video_breite} x {video_hoehe} / {frame_rate}f) {codec_version}\n"
        )
        return content

    def files_load(self, filename):
        self.Btn_copy_infodatas.setVisible(True)
        if filename is None:
            inhalt = f"{'Format':18}= FULLHD 1080p\n" \
                     f"{'Resize':18}=\n" \
                     f"{'Laufzeit':18}=" 
            self.lblnfoDaten.setText(inhalt)
        else:
            self.lbl_movie_file.setText(filename)
            filename = filename.replace("/", "\\")
            win_folder, win_file = self.get_file_details(filename)
            file_size = re.sub(r"\s+", "", win_folder.GetDetailsOf(win_file, 1))
            file = win_folder.GetDetailsOf(win_file, 165)[0:-4]            
            ms_codec = win_folder.GetDetailsOf(win_file, 311)
            codec_version = self.get_video_codec(ms_codec)

            if codec_version is None:
                video_breite, video_hoehe, bitrate, runtime, frame_rate, format, codec_version = ["000"] * 7
            else:
                video_breite, video_hoehe, bitrate, runtime, frame_rate = self.get_video_properties(win_folder, win_file)
                Format = self.get_format_resolution(video_hoehe)

            inhalt = self.build_content_format(file_size, video_breite, video_hoehe, bitrate, frame_rate, codec_version) + \
                    f"{'Laufzeit':18}= {runtime}"

            self.lbl_movie_title.setText(file)
            self.lblnfoDaten.setText(inhalt)

        pyperclip.copy(inhalt)

        

    ###----------------- zurück zum Hauptmenu per Button --------------------------------###
    ###----------------------------------------------------------------------------------###
    def stacked_back(self):
        ###-------------------------Fenster Anzeigen.-----------------------------------------###
        ### ----------------------------------------------------------------------------------###
        self.stackedWidget.setCurrentIndex(0)
        self.set_button_visible(False)

    def internet_output(self):
        ###-------------------------Fenster Anzeigen.-----------------------------------------###
        ### ----------------------------------------------------------------------------------###
        self.stackedWidget.setCurrentWidget(self.internet)
        self.Btn_set_nfo_mask.setHidden(True) 
        ###-------------------------auf Klicks reagieren--------------------------------------###
        self.Btn_back.clicked.connect(self.stacked_back)
        self.Btn_set_nfo_mask.clicked.connect(self.set_nfo_mask)        
        
    def set_button_visible(self,Status):        
        self.CopyBtn_InfoDatei.setVisible(Status)
        self.EditBtn_AKA.setVisible(Status)
        self.CopyBtn_InfoAKA.setVisible(Status)
        self.Btn_copy_infodatas.setVisible(Status)
        self.CopyBtn_InfoDarsteller.setVisible(Status)
        self.EditBtn_Darsteller.setVisible(Status)
        self.Btn_nfo_maker.setVisible(Status)

    def get_url_infos(self):
        img_path: str=""
        self.set_buttons_enabled(False)
        url = self.lnEdit_scrape_url.text() 

        if url.startswith("https://www.iafd.com"):
            img_path = ":/internet/internet/IAFD.jpg"            
            website="IAFD"
        elif url.startswith("https://www.imdb.com/title/"):
            img_path = ":/internet/internet/images/IMDb.png"
            website="IMDb" 
        else:
            return 
        self.internet_output()
        content = Scraping().open_url(url)      
        self.lbl_INTLogo.setPixmap(QPixmap(img_path))
        QApplication.processEvents()
        ### --------------------------------- Titel                     ------------------------------------- ###
        title, serie = Scraping().get_movie_title(website, content)          
        self.lbl_INTName.setText(title)
        ### --------------------------------- Regie                     ------------------------------------- ###
        Regie=Scraping().get_regie(website, content)
        self.lbl_INTRegie.setText(Regie)
        ### --------------------------------- Land                      ------------------------------------- ###
        Land=Scraping().get_country(website, content) 
        self.lbl_INTLand.setText(Land)
        ### --------------------------------- Label und Distributor     ------------------------------------- ###             
        Distributor=Scraping().get_label(website, content)
        self.lbl_INTLabel.setText(Distributor)
        ### --------------------------------- Release-Datum -------------------------------------------------- ### 
        ReleaseDate=Scraping().get_releasedate(website, content)
        with open(Path(__file__).absolute().parent / "JSON/url.json", 'r') as f:
            infos=json.load(f)  
        self.lbl_INTDatum.setText(ReleaseDate)
        ### --------------------------------- AKA in eine Tabelle laden -------------------------------------- ###        
        ###--------------------------------------------------------------------------------------------------- ### 
        if "imdb.com" in url[:20]:
            content = Scraping().open_url(infos["akaLink"])            
        also_known_as_all = Scraping().get_aka(website, content)
        if not also_known_as_all:
            status_fehler_ausgabe(self, "AKA: Keine Daten !")                        
        self.tbl_INTAKA.setRowCount(len(also_known_as_all))
        for row, also_known_as in enumerate(also_known_as_all):                        
            self.tbl_INTAKA.setItem(row, 0, QTableWidgetItem(str(also_known_as[0])))
            self.tbl_INTAKA.setItem(row, 1, QTableWidgetItem(str(also_known_as[1])))
            self.tbl_INTAKA.setItem(row, 2, QTableWidgetItem(str(also_known_as[2])))
        ### --------------------------------- Szenen in eine Tabelle packen ----------------------------------- ###
        scenen = Scraping().get_scenen(website, content)
        self.tbl_INTHandlung.setRowCount(len(scenen))
        for row, scene in enumerate(scenen):
            self.tbl_INTHandlung.setItem(row, 0, QTableWidgetItem(f"{scene['nr']}"))
            self.tbl_INTHandlung.setItem(row, 3, QTableWidgetItem(f"{scene['name']}"))
        ### --------------------------------- Darsteller in eine Tabelle packen-------------------------------- ###
        if "imdb.com" in url[:20] and infos.get("DarstellerLink")!="":
            content = Scraping().open_url(infos["DarstellerLink"])    
        artists = Scraping().get_performers(website, content)                        
        self.tbl_INTDarsteller.setRowCount(len(artists))
        for reihe, item in enumerate(artists):                   
            self.tbl_INTDarsteller.setItem(reihe, 0, QTableWidgetItem(item.get('name', '')))
            self.tbl_INTDarsteller.setItem(reihe, 1, QTableWidgetItem(item.get('alias', ''))) 
            self.tbl_INTDarsteller.setItem(reihe, 2, QTableWidgetItem(item.get('skill', ''))) 
        ### --------------------------------------------------------------------------------------------------- ### 
        self.Btn_set_nfo_mask.setHidden(False)
        self.set_buttons_enabled(True)

    def set_buttons_enabled(self, status: bool):
        self.Btn_get_url_infos.setEnabled(status)
        self.Btn_back.setEnabled(status)
        
    def set_nfo_mask(self):
        if self.lnEdit_scrape_url.text().startswith("https://www.iafd.com"):
            self.InhaltLoeschen()
        serie: str=""
        ### -------------------------------Titel ------------------------------------------------------ ### 
        ergebnis = self.set_title()     
        ### ------------------------------- Anhand des Titel prüfen ob Serie -------------------------- ###        
        if ergebnis[len(ergebnis):-1].isdigit():
            serie = [ergebnis[:-1].rfind(" ")]
        ### ------------------------------- Regie --------------------------------------- ###        
        ergebnis = self.set_regie()                                    
        self.lbl_movie_regie.setText(ergebnis)
        ### ------------------------------- Studio --------------------------------------- ###
        ergebnis = self.set_studio()                      
        self.lbl_movie_studio.setText(ergebnis)
        ### ------------------------------- Release Datum --------------------------------------- ###
        ergebnis = self.set_release_date()                   
        self.lbl_movie_releasedate.setText(ergebnis)
        if not self.lbl_movie_serie.text():
            self.lbl_movie_serie.setText(serie)
        self.set_country()                
          ### ------------------------------- Tabelle AKA --------------------------------------------- ###                    
        self.set_also_known_as()                        
        ### ------------------------------- Tabelle Darsteller ---------------------------------------- ###                
        self.set_artist_list()                       
        ### ------------------------------- Scene / Handlung --------------------------------------------- ###
        self.set_scenen_list()  
        ### ------------------------------- Links ------------------------------------------------------ ###        
        self.lblLinks.setText(f"{self.lblLinks.text()}{self.lnEdit_scrape_url.text()}\n")
        ### ------------------------------- Anzeige Titel-Fenster und Inhalt löschen ------------------- ###        
        self.stackedWidget.setCurrentIndex(0)
        self.set_button_visible(True)

    def set_title(self): 
        releasedate=self.lbl_INTDatum.text()
        studio = self.lbl_INTLabel.text()
        title: str = self.lbl_INTName.text()
        if re.search(r'\((\d{4})\)$', title):
           releasedate = self.lbl_INTName.text()[-6:]
        title = title.replace(releasedate,"").strip()                                
        self.lbl_movie_title.setText(f"{studio} - {title}{releasedate}FULLHD-ENGLISH")
        return title
    
    def set_regie(self):        
        self.lbl_movie_regie.setText(self.lbl_INTRegie.text())            
        return self.lbl_INTRegie.text()
    
    def set_studio(self):
        self.lbl_movie_studio.setText(self.lbl_INTLabel.text())         
        return self.lbl_INTLabel.text()
    
    def set_country(self):
        for num in range(len(self.Land_CheckcBox)):            
            if self.Land_CheckcBox.model().item(num, 0).text() == self.lbl_INTLand.text():
                item = self.Land_CheckcBox.model().item(num, 0)
                item.setCheckState(Qt.CheckState.Checked)
    
    def set_release_date(self):
        self.lbl_movie_releasedate.setText(self.lbl_INTDatum.text())        
        return self.lbl_INTDatum.text()
    
    def set_also_known_as(self):
        table_also_known_as: dict = {}
        table_also_known_as_from_web: dict={}
        for row in range(self.tblAKA.rowCount()):
            title = self.tblAKA.item(row, 0).text()
            country_type = self.tblAKA.item(row, 1).text()
            country = self.tblAKA.item(row, 2).text()            
            also_known_as_dict = {title: (country_type, country)}
            table_also_known_as.update(also_known_as_dict)        
        for row in range(self.tbl_INTAKA.rowCount()):
            title = self.tbl_INTAKA.item(row, 0).text()
            country_type = self.tbl_INTAKA.item(row, 1).text()
            country = self.tbl_INTAKA.item(row, 2).text()            
            also_known_as_dict = {title: (country_type, country)}           
            table_also_known_as_from_web.update(also_known_as_dict)        
        for name, country_type in table_also_known_as_from_web.items():
            if name not in table_also_known_as:
                new_row = self.tblAKA.rowCount() + 1
                self.tblAKA.setRowCount(new_row)
                self.tblAKA.setItem(new_row-1, 0,QTableWidgetItem(name))                               
                self.tblAKA.setItem(new_row-1, 1,QTableWidgetItem(country_type[0]))
                self.tblAKA.setItem(new_row-1, 2,QTableWidgetItem(country_type[1]))

    def set_artist_list(self):
        table_artist: dict = {}
        table_artist_from_web: dict={}
        for row in range(self.tblDarsteller.rowCount()):
            actor_name = self.tblDarsteller.item(row, 0).text()
            actor_role_name = self.tblDarsteller.item(row, 1).text()
            actor_alias = self.tblDarsteller.item(row, 2).text()
            actor_type = self.tblDarsteller.item(row, 3).text()
            actor_list = {actor_name: (actor_role_name, actor_alias, actor_type)}            
            table_artist.update(actor_list)
        for row in range(self.tbl_INTDarsteller.rowCount()):
            actor_name = self.tbl_INTDarsteller.item(row, 0).text()
            actor_role_name = self.tbl_INTDarsteller.item(row, 1).text() if self.tbl_INTDarsteller.item(row, 1) else ""
            actor_alias = self.tbl_INTDarsteller.item(row, 2).text() if self.tbl_INTDarsteller.item(row, 2) else ""
            actor_type = self.tbl_INTDarsteller.item(row, 3).text() if self.tbl_INTDarsteller.item(row, 3) else ""
            actor_list = {actor_name: (actor_role_name, actor_alias, actor_type)} 
            table_artist_from_web.update(actor_list)
        for name, rolle_alias_type in table_artist_from_web.items():
            if name not in table_artist:                
                new_row = self.tblDarsteller.rowCount()+1
                self.tblDarsteller.setRowCount(new_row)
                self.tblDarsteller.setItem(new_row-1, 0,QTableWidgetItem(name))                
                self.tblDarsteller.setItem(new_row-1, 1,QTableWidgetItem(rolle_alias_type[0]))
                self.tblDarsteller.setItem(new_row-1, 2,QTableWidgetItem(rolle_alias_type[1]))
                self.tblDarsteller.setItem(new_row-1, 3,QTableWidgetItem(rolle_alias_type[2])) 

    def set_scenen_list(self):
        scenen=""
        if self.tbl_INTHandlung.rowCount() > 0:
            for row in range(self.tbl_INTHandlung.rowCount()):
                scenen += f"Szene {row+1}: {self.tbl_INTHandlung.item(row, 3).text()}\n"
            self.lblHandlung.setText(scenen)  
    
    def nfo_maker(self):
        ###------------------------ von Tabelle Darsteller in String umwandeln --------------------------###
        actor = self.artists_table()
        also_know_as = self.set_also_know_as_in_table()
        label=f"{'Regie':18}= {self.lbl_movie_regie.text()}\n" \
              f"{'Label':18}= {self.lbl_movie_studio.text()}\n" \
              f"{'Serie':18}= {self.lbl_movie_serie.text()}\n" \
              f"{'Erscheinungsdatum':18}= {self.lbl_movie_releasedate.text()}"
        ###------------------------- nfo speichern und ins Movie Ordner schieben ------------------------###
        with open(Path(__file__).absolute().parent /'nfo.txt', 'w+', encoding='utf-8') as nfo_items:
            nfo_items.write(self.get_nfo_format(label, also_know_as, actor))

        destination_folder = Path(self.lbl_movie_file.text())
        source = Path(__file__).parent / 'nfo.txt'
        destination = destination_folder.parent / 'nfo.txt'                  
        shutil.move(source, destination)
        os.system(f"start notepad.exe {destination}")

    def get_nfo_format(self, label, also_know_as, actor):
        title = self.lbl_movie_title.text()
        return  f"{title}\n{'-'*len(title)}\n" \
                f"AKA:\n{also_know_as}\n" \
                f"Links:\n{self.lblLinks.text()}\n\n" \
                f"{label}\n{self.lblnfoDaten.text()}\n" \
                f"{'Sprache':18}= englisch\n" \
                f"{'Land':18}= USA\n\n" \
                f"{actor}\n" \
                f"Handlung:\n{self.lblHandlung.text()}"

    
    def nfo_file_load(self):
        destination = self.get_file_datas("nfo")
        try: 
            with open(destination,'r') as file:
                nfo = file.read().split("\n")
            movie_title = nfo[0]
            also_know_as: list=[]
            
            if nfo[2]=="AKA":
                for index in range(2,len(nfo)):
                    if nfo[index]=="Links:":                                        
                        for i in range(3,index):                                                
                            if nfo[i].strip()!="":also_know_as.append(nfo[i].strip())
                print(f"AKAs: {also_know_as}\n")
        except:
            print("keine Datei gefunden")

    def get_file_datas_Laden(self):
        self.files_load(self.get_file_datas("Video"))
        

    def set_also_know_as_in_table(self):
        also_known_as:str="" 
        for row in range(self.tblAKA.rowCount()):
            also_known_as += self.build_aka_string(row) 
        return also_known_as
    
    def build_aka_string(self, row):
        title_alias = self.tblAKA.item(row, 0).text()
        title_type = f"Titel in {self.tblAKA.item(row, 1).text()}" if self.tblAKA.item(row, 1).text() else ""
        country_prefix = f"{self.tblAKA.item(row, 2).text()}: " if self.tblAKA.item(row, 2).text() else ""

        return f"{title_type}{country_prefix}{title_alias}"

    def artists_table(self):

        headers = ["Darsteller", "Rollenname", "Alias", "Art"]
        widths = [0, 0, 0, 0]

        for col, header in enumerate(headers):
            widths[col] = len(header)
            for row in range(self.tblDarsteller.rowCount()):
                cell = self.tblDarsteller.item(row, col).text()
                widths[col] = max(widths[col], len(cell))

        table = f"╔{'═' * (sum(widths) + 11)}╗\n"
        table += f"║ {'Darsteller':{sum(widths)+ 9}} ║\n╠"

        for col, width in enumerate(widths):
            if col > 0:
                table += "╦" if width > 0 else "═"
            table += f"{'═' * (width + 2)}"
        
        table += "╣\n"
        
        for row in range(self.tblDarsteller.rowCount()):
            for col, width in enumerate(widths):
                cell = self.tblDarsteller.item(row, col).text()
                table += f"║ {cell:>{width}} "
            table += "║\n"
        table += "╚"
        for col, width in enumerate(widths):
            if col > 0:
                table += "╩" if width > 0 else "═"
            table += f"{'═' * (width + 2)}"

        return f"{table}╝"

    def CopyClipboard_InfoDatei(self):
        pyperclip.copy(self.lbl_movie_title.text())
    def CopyClipboard_InfoDaten(self):
        pyperclip.copy(self.lblnfoDaten.text())
    def CopyClipboard_InfoAKA(self):
        also_known_as=self.set_also_know_as_in_table()
        pyperclip.copy(f"{also_known_as}\n" \
                       f"Links:\n{self.lblLinks.text()}\n\n" \
                       f"{self.lbl_movie_studio.text()}"    )
    def CopyClipboard_InfoDarsteller(self):
        artists_in_table=self.artists_table()
        pyperclip.copy(f"\n{artists_in_table}\n" \
                       f"Handlung:\n{self.lblHandlung.text()}")



# Abschluss
if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = Haupt_Fenster() 
    MainWindow.show()   
    app.exec()