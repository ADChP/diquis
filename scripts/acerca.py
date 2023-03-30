'''

Diquís
Complemento para labores internas en Telespazio Costa Rica.

Archivo de la ventana de Acerca y su contenido.

Autor: Andrés David Chavarría-Palma
Marzo - 2023

'''
import os
from .acerca_ui import acercaUI

class Acerca:
   acercaUI = acercaUI()

   def acerca_ventana(self):
    Acerca.acercaUI.acerca.clear()
    Acerca.acercaUI.acerca.setAcceptRichText(True)
    Acerca.acercaUI.acerca.setOpenExternalLinks(True)
    adjunto1= os.path.dirname(os.path.realpath(__file__)) + '/stone_sphere.jpg'
    html_text = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head>'''+f'''<body style=" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;">
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:18pt; font-weight:600;">Diquís</span></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt;">Complemento para labores internas en Telespazio Costa Rica.</span></p>
<p align="center" style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;"><br /></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt;">Autor: </span><a href="https://github.com/ADChP"><span style=" font-size:12pt; text-decoration: underline; color:#d1392b;">Andrés David Chavarría-Palma</span></a></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-style:italic;">andres.chavarria@tpzcr.com</span></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt;">2023.03.30</span></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt;">Versión: 0.1 (Beta)</span></p>
<p align="center" style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;"><br /></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><img src="{adjunto1}" /></p></body></html>'''
    Acerca.acercaUI.acerca.append(html_text)
    Acerca.acercaUI.show()