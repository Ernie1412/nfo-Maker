from PyQt6.QtWidgets import QStatusBar
from PyQt6.QtCore import QDateTime, QTimer


def StatusBar(self,text: str, farbe: str) -> None:  
    self.statusBar = QStatusBar()
    zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
    self.statusBar.showMessage(f"ℹ️ {zeit}: {text}")         
    self.statusBar.setStyleSheet(f"border :1px solid ;background-color : {farbe}")
    self.setStatusBar(self.statusBar) 
    QTimer.singleShot(4500, lambda :self.statusBar.setStyleSheet("background-color : #fffdb7"))  

def status_fehler_ausgabe(self, message: str) -> None:
    StatusBar(self, message,"#F78181")                       
    QTimer.singleShot(500, lambda :StatusBar(self, message,"#fffdb7"))
    QTimer.singleShot(1000, lambda :StatusBar(self, message,"#F78181"))
    QTimer.singleShot(1500, lambda :StatusBar(self, message,"#fffdb7"))