'''

Diquís
Complemento para labores internas en Telespazio Costa Rica.

Archivo de publicación del complemento.

Autor: Andrés David Chavarría-Palma
Marzo - 2023

'''
from .scripts.main import DiquisPlugin

def classFactory(iface):
    return DiquisPlugin(iface)