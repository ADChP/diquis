'''

Diquis
Complemento para labores internas en Telespazio Costa Rica.

Archivo de compilado del archivo UI para la función de planos Sin Sector Circular.

Autor: Jason Alberto Navarro Ulate
       Andrés David Chavarría-Palma
       
Creado el: Martes 4 de abril del 2023
Actualziado el: 
Version: 0.1

'''


import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'planossinsectorcircular.ui'))

class psscUI(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(psscUI, self).__init__(parent)
        self.setupUi(self)
