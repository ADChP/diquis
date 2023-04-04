'''

Diquís
Complemento para labores internas en Telespazio Costa Rica.

Archivo de arranque del complemento, interfaz gráfica y herramientas.

Autor: Andrés David Chavarría-Palma
Marzo - 2023

'''
from PyQt5.QtWidgets import QAction, QMenu
from .inconsistencia6 import Inconsistencia6
from .inconsistencia7 import Inconsistencia7
from .acerca import Acerca

class DiquisPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.menu = QMenu(self.iface.mainWindow())
        self.menu.setTitle("Telespazio CR")

        self.action1 = QAction('Inconsistencia 6', self.iface.mainWindow())
        self.action1.triggered.connect(Inconsistencia6.tools)

        self.action2 = QAction('Inconsistencia 7', self.iface.mainWindow())
        self.action2.triggered.connect(Inconsistencia7.tools)

        self.action3 = QAction('Acerca de', self.iface.mainWindow())
        self.action3.triggered.connect(Acerca.acerca_ventana)
        
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)

        menuBar = self.iface.mainWindow().menuBar()
        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(),self.menu)

    def unload(self):
        self.menu.deleteLater()
        del self.action1, self.action2, self.action3