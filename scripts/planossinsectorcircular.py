'''

Diquis
Complemento para labores internas en Telespazio Costa Rica.

Archivo de la clase Planos sin sector circular y sus herramientas.

Autor: Jason Alberto Navarro Ulate
       Andrés David Chavarría-Palma
       
Creado el: Lunes 3 de abril del 2023
Actualziado el: 
Version: 0.1

'''

import processing
from qgis.core import QgsMapLayerProxyModel
from qgis.core import QgsProcessing
from qgis.core import QgsProject
from qgis.utils import iface
from PyQt5.QtWidgets import QProgressBar
from .planossinsectorcircular_ui import psscUI

class PlanosSinSectorCircular():
    pssc = psscUI()
    
    #Función para activar o desactivar el boton aceptar para ejecutar el geopreceso
    def activarBoton(self):
        if (len(PlanosSinSectorCircular.pssc.coddist.text()) == 5) and PlanosSinSectorCircular.pssc.coddist.text().isdigit():
            PlanosSinSectorCircular.pssc.button_box.setEnabled(True)
        else:
            PlanosSinSectorCircular.pssc.button_box.setEnabled(False)
    
    #Función de botones de entrada para ejecución del algoritmo: Mosaico Catastral, Vias, Tabla de Inconsistencia Conciliación
    def tools(self):
        PlanosSinSectorCircular.pssc.pe.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        PlanosSinSectorCircular.pssc.pl.setFilters(QgsMapLayerProxyModel.NoGeometry)
        PlanosSinSectorCircular.pssc.coddist.textChanged.connect(PlanosSinSectorCircular.activarBoton)
        PlanosSinSectorCircular.pssc.show()
        result = PlanosSinSectorCircular.pssc.exec_()
        if result:
            #Barra de progreso
            barra_mensaje = iface.messageBar().createMessage('En proceso...')
            barra = QProgressBar()
            barra.setMaximum(100)
            barra_mensaje.layout().addWidget(barra)
            iface.messageBar().pushWidget(barra_mensaje)
            
            #Variables de entrada
            txt_codigo = PlanosSinSectorCircular.pssc.coddist.text()
            planos =  PlanosSinSectorCircular.pssc.pl.currentLayer()
            planos_escalados = PlanosSinSectorCircular.pssc.pe.currentLayer()
            prog_bar = 20
            barra.setValue(prog_bar)
            prog_bar += 20
            
            #Rehacer campos de entrada
            alg_params0 = {
                'FIELDS_MAPPING': [{'expression': 'Planos_Provincia','length': 0,'name': 'Provincia','precision': 0,'sub_type': 0,'type': 0,'type_name': ''},
                                   {'expression': "CASE \r\nWHEN Planos_Canton <= 9 THEN '0' || Planos_Canton\r\nELSE\r\nPlanos_Canton\r\nEND",'length': 0,'name': 'Canton','precision': 0,'sub_type': 0,'type': 0,'type_name': ''},
                                   {'expression': "CASE\r\nWHEN Planos_Distrito <= 9 THEN '0' || Planos_Distrito\r\nELSE Planos_Distrito\r\nEND",'length': 0,'name': 'Distrito','precision': 0,'sub_type': 0,'type': 0,'type_name': ''},
                                   {'expression': 'Planos_Id','length': 0,'name': 'Planos_Id','precision': 0,'sub_type': 0,'type': 0,'type_name': ''},
                                   {'expression': 'Planos_Numero','length': 0,'name': 'Planos_Numero','precision': 0,'sub_type': 0,'type': 0,'type_name': ''},
                                   {'expression': 'Planos_Fecha','length': 0,'name': 'Planos_Fecha','precision': 0,'sub_type': 0,'type': 0,'type_name': ''},
                                   {'expression': 'Planos_Conciliado','length': 0,'name': 'Planos_Conciliados','precision': 0,'sub_type': 0,'type': 0,'type_name': ''},
                                   {'expression': 'Planos_DerroteroSectorCircular','length': 0,'name': 'Planos_DerroteroSectorCircular','precision': 0,'sub_type': 0,'type': 0,'type_name': ''},
                                   {'expression': 'Planos_AreaM2','length': 0,'name': 'Planos_AreaM2','precision': 0,'sub_type': 0,'type': 0,'type_name': ''}],
                'INPUT': planos,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs0 = processing.run('native:refactorfields', alg_params0)
            outputs0 = outputs0['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 20
           
            #Rehacer campos para tener el coddist correcto para extraer
            alg_params1 = {
                'FIELDS_MAPPING': [{'expression': 'Provincia || Canton || Distrito','length': 0,'name': 'coddist','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': 'Planos_Id','length': 0,'name': 'Plano','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': 'Planos_Numero','length': 0,'name': 'Plano_Numero','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': 'Planos_Fecha','length': 0,'name': 'Plano_Fecha','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': 'Planos_Conciliados','length': 0,'name': 'Conciliados','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': 'Planos_DerroteroSectorCircular','length': 0,'name': 'Sector_Circular','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': 'Planos_AreaM2','length': 0,'name': 'Area','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs0,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs1 = processing.run('native:refactorfields', alg_params1)
            outputs1 = outputs1['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 20
            
            #Extraer por expresión para la capa de planos (sin geometría)
            alg_params2 = {
                'EXPRESSION': f"coddist like trim('{txt_codigo}') AND Sector_Circular = 'S' AND Conciliados = 'S'",
                'INPUT': outputs1,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs2 = processing.run('native:extractbyexpression', alg_params2)
            outputs2 = outputs2['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 20
            
            # Unir atributos por valor de campo outputs 1 y entrada planos
            alg_params3 = {
                'DISCARD_NONMATCHING': True,
                'FIELD': 'Plano',
                'FIELDS_TO_COPY': [''],
                'FIELD_2': 'plano',
                'INPUT': outputs2,
                'INPUT_2': planos_escalados,
                'METHOD': 0,  # Crear objeto separado para cada objeto coincidente (uno a muchos)
                'PREFIX': '',
                'NON_MATCHING': QgsProcessing.TEMPORARY_OUTPUT,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs3 = processing.run('native:joinattributestable', alg_params3)
            outputs3a = outputs3['OUTPUT']
            outputs3b = outputs3['NON_MATCHING']
            barra.setValue(prog_bar)
            prog_bar += 20
            
            #Rehacer campos No Marcados
            alg_params4 = {
                'FIELDS_MAPPING': [{'expression': '"coddist"','length': 0,'name': 'coddist','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Plano"','length': 0,'name': 'Plano','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Plano_Numero"','length': 0,'name': 'Plano_Numero','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Plano_Fecha"','length': 0,'name': 'Plano_Fecha','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Conciliados"','length': 0,'name': 'Conciliados','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Sector_Circular"','length': 0,'name': 'Sector_Circular_en_Aplicativo','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': "'No'",'length': 0,'name': 'Sector_Circular_en_Capa_PostGis','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Area"','length': 0,'name': 'Area','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs3b,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs4 = processing.run('native:refactorfields', alg_params4)
            outputs4 = outputs4['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 20
            
            #Rehacer campos Marcados
            alg_params5 = {
                'FIELDS_MAPPING': [{'expression': '"coddist"','length': 0,'name': 'coddist','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Plano"','length': 0,'name': 'Plano','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Plano_Numero"','length': 0,'name': 'Plano_Numero','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Plano_Fecha"','length': 0,'name': 'Plano_Fecha','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Conciliados"','length': 0,'name': 'Conciliados','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Sector_Circular"','length': 0,'name': 'Sector_Circular_en_Aplicativo','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': "'Marcado'",'length': 0,'name': 'Sector_Circular_en_capa_PostGis','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"perimetro"','length': -1,'name': 'perimetro','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'},
                                   {'expression': '"Area"','length': 0,'name': 'Area','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"usuariocreador"','length': 50,'name': 'usuariocreador','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"fechacreacion"','length': -1,'name': 'fechacreacion','precision': 0,'sub_type': 0,'type': 16,'type_name': 'datetime'},
                                   {'expression': '"fechaedicion"','length': -1,'name': 'fechaedicion','precision': 0,'sub_type': 0,'type': 16,'type_name': 'datetime'},
                                   {'expression': '"usuarioeditor"','length': 50,'name': 'usuarioeditor','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs3a,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs5 = processing.run('native:refactorfields', alg_params5)
            outputs5 = outputs5['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 20
            
            #Salidas finales
            outputs4.setName('Sector Circular No Dibujado - Revisar')
            outputs5.setName('Sector Circular Dibujado')
            QgsProject.instance().addMapLayer(outputs4)
            QgsProject.instance().addMapLayer(outputs5)
            
            #Eliminar temporales no necesarios
            del outputs0,outputs1,outputs2
            
            barra.setValue(prog_bar)
            iface.messageBar().clearWidgets()
            iface.messageBar().pushSuccess('Planos sin Sector Circular', 'Finalizado correctamente')