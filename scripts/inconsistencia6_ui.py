"""

Diquís
Complemento para labores internas en Telespazio Costa Rica.

Archivo de compilado del archivo UI para la función de incosistencia # 6.

Autor: Andrés David Chavarría-Palma

Marzo - 2023

"""
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'inconsistencia6.ui'))

class incon6UI(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(incon6UI, self).__init__(parent)
        self.setupUi(self)
