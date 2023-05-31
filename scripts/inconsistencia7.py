'''

Diquis
Complemento para labores internas en Telespazio Costa Rica.

Archivo de la clase Inconsistencia 7 y sus herramientas.

Autor: Jason Alberto Navarro Ulate
       Andrés David Chavarría-Palma
       
Creado el: Lunes 3 de abril del 2023
Actualziado el: 
Version: 0.1

'''

import processing
from qgis.core import QgsMapLayerProxyModel
from qgis.core import QgsProcessing
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsProject
from qgis.utils import iface
from PyQt5.QtWidgets import QProgressBar
from .inconsistencia7_ui import incon7UI


class Inconsistencia7():
    inc7 = incon7UI()
    
    #Función para activar o desactivar el boton aceptar para ejecutar el geopreceso
    def activarBoton(self):
        if (len(Inconsistencia7.inc7.bloque.text()) == 8 or len(Inconsistencia7.inc7.bloque.text()) == 5) and Inconsistencia7.inc7.bloque.text().isdigit():
            Inconsistencia7.inc7.button_box.setEnabled(True)
        else:
            Inconsistencia7.inc7.button_box.setEnabled(False)
            
    #Función de botones de entrada para ejecución del algoritmo: Mosaico Catastral, Vias, Tabla de Inconsistencia Conciliación
    def tools(self):
        Inconsistencia7.inc7.mc.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        Inconsistencia7.inc7.vs.setFilters(QgsMapLayerProxyModel.LineLayer)
        Inconsistencia7.inc7.ic.setFilters(QgsMapLayerProxyModel.NoGeometry)
        Inconsistencia7.inc7.bloque.textChanged.connect(Inconsistencia7.activarBoton)
        Inconsistencia7.inc7.show()
        result = Inconsistencia7.inc7.exec_()
        
        if result:
            #Barra de progreso
            barra_mensaje = iface.messageBar().createMessage('En proceso...')
            barra = QProgressBar()
            barra.setMaximum(100)
            barra_mensaje.layout().addWidget(barra)
            iface.messageBar().pushWidget(barra_mensaje)
            
            #Variables de entrada
            txt_codigo = Inconsistencia7.inc7.bloque.text()
            mosai_catas = Inconsistencia7.inc7.mc.currentLayer()
            vias = Inconsistencia7.inc7.vs.currentLayer()
            incon_conci = Inconsistencia7.inc7.ic.currentLayer()
            
            prog_bar = 3
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Extraer por expresión: Se extraen los datos de todo el distrito concerniente al bloque elegido
            if len(txt_codigo) == 5:
                expres_alg_params0 = f"bloque like trim('{txt_codigo}') || '%'"
            else:
                expres_alg_params0 = f"bloque like substr('{txt_codigo}',1,5) || '%'"
            alg_params0 = {'EXPRESSION': expres_alg_params0,
                           'INPUT': mosai_catas,
                           'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs0 = processing.run('native:extractbyexpression', alg_params0)
            outputs0 = outputs0['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Extraer por expresión: Se extraen los polígonos marcados como vías en el mosaico catastral
            #expres_alg_params1 = "identificdor like '%V'"
            alg_params1 = {'EXPRESSION': "identificador like '%V'",
                           'INPUT': mosai_catas,
                           'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs1 = processing.run('native:extractbyexpression', alg_params1)
            outputs1 = outputs1['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Buffer negativo
            alg_params2 = {
                'DISSOLVE': False,
                'DISTANCE': -0.85,
                'END_CAP_STYLE': 2,  # Cuadrado
                'INPUT': outputs0,
                'JOIN_STYLE': 1,  # Inglete
                'MITER_LIMIT': 2,
                'SEGMENTS': 5,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs2 = processing.run('native:buffer', alg_params2)
            outputs2 = outputs2['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Disuelto de vías
            alg_params3 = {
                'INPUT': vias,
                'SEPARATE_DISJOINT': False,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs3 = processing.run('native:dissolve', alg_params3)
            outputs3 = outputs3['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Corregir geometrías del outputs1 (mosaico catastral que tiene la V)
            alg_params4 = {
                'INPUT': outputs1,
                'METHOD': 1,  # Structure
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs4 = processing.run('native:fixgeometries', alg_params4)
            outputs4 = outputs4['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Polígonos a líneas del mosaico catastral (geometrías corregidas = outputs4)
            alg_params5 = {
                'INPUT': outputs4,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs5 = processing.run('native:polygonstolines', alg_params5)
            outputs5 = outputs5['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Intersección Vias de Mosaico con el buffer negativo (outputs 4 y outputs 2 )
            alg_params6 = {
                'GRID_SIZE': None,
                'INPUT': outputs5,
                'OVERLAY': outputs2,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs6 = processing.run('native:intersection', alg_params6)
            outputs6 = outputs6['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Intersección Disuelto con el Buffer Negativo (outputs 3 y outputs 2)
            alg_params7 = {
                'GRID_SIZE': None,
                'INPUT': outputs3,
                'OVERLAY': outputs2,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs7 = processing.run('native:intersection', alg_params7)
            outputs7 = outputs7['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Extraer por expresión. Filtrar el resultado de la intersección entre mosaico vias y buffer para ver resultado (outputs 6)
            alg_params8 = {
                'EXPRESSION': '"identificador" != "identificador_2"',
                'INPUT': outputs6,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs8 = processing.run('native:extractbyexpression', alg_params8)
            outputs8 = outputs8['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Rehacer campos del output 8 que es la salida del extraer por expresión de la intersección entre vias mosaico y buffer negativo
            alg_params9 = {
                'FIELDS_MAPPING': [{'expression': '"identificador_2"','length': 0,'name': 'Identificador','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"bloque_2"','length': 0,'name': 'Bloque','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs8,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs9 = processing.run('native:refactorfields', alg_params9)
            outputs9 = outputs9['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Rehacer campos del output 7 que es la salida de la intersección entre el disuelto y el buffer negativo
            alg_params10 = {
                'FIELDS_MAPPING': [{'expression': '"identificador"','length': 0,'name': 'Identificador','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"bloque"','length': 0,'name': 'Bloque','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs7,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs10 = processing.run('native:refactorfields', alg_params10)
            outputs10 = outputs10['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Extraer por bloque o distrito: Capa final 1 de traslapes entre disuelto (vías) y buffer negativo
            if len(txt_codigo) == 8:
                alg_params11 = {
                    'EXPRESSION': f"Bloque like '{txt_codigo}'",
                    'INPUT': outputs10,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
                outputs11 = processing.run('native:extractbyexpression', alg_params11)
                outputs11 = outputs11['OUTPUT']
            else:
                outputs11=outputs10   
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Extraer por bloque o distrito: Capa final 2 de traslapes entre mosaico (vías) y buffer negativo
            if len(txt_codigo) == 8:
                alg_params12 = {
                    'EXPRESSION': f"Bloque like '{txt_codigo}'",
                    'INPUT': outputs9,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
                outputs12 = processing.run('native:extractbyexpression', alg_params12)
                outputs12 = outputs12['OUTPUT']
            else:
                outputs12=outputs9   
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Union entre capa final 1 (outputs 11) y la tabla InconsistenciasConciliacion para verificar los traslapes no marcados en el sistema y que deberían revisarse
            alg_params13 = {
                'DISCARD_NONMATCHING': False,
                'FIELD': 'Identificador',
                'FIELD_2': 'InconsConc_IdPredial',
                'INPUT': outputs11,
                'INPUT_2': incon_conci,
                'METHOD': 1,  # Tomar solo los atributos del primer objeto coincidente (uno a uno)
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs13 = processing.run('native:joinattributestable', alg_params13)
            outputs13 = outputs13['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Union entre capa final 2 (outputs 12) y la tabla InconsistenciasConciliacion para verificar los traslapes no marcados en el sistema y que deberían revisarse
            alg_params14 = {
                'DISCARD_NONMATCHING': False,
                'FIELD': 'Identificador',
                'FIELD_2': 'InconsConc_IdPredial',
                'INPUT': outputs12,
                'INPUT_2': incon_conci,
                'METHOD': 0,  # Crear objeto separado para cada objeto coincidente (uno a muchos)
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs14 = processing.run('native:joinattributestable', alg_params14)
            outputs14 = outputs14['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Filtra y separa los predios como marcados y no marcados entre lo espacial y lo indicado en el sistema (outputs 13)
            alg_params15 = {
                'EXPRESSION': "(InconsConc_IdPredial is NULL) or (InconsConc_IdPredial is not NULL and (InconsConc_Incon07 not like '7%' or InconsConc_Incon07 is NULL))",
                'INPUT': outputs13,
                'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs15 = processing.run('native:extractbyexpression', alg_params15)
            outputs15a = outputs15['OUTPUT']
            outputs15b = outputs15['FAIL_OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Filtra y separa los predios como marcados y no marcados entre lo espacial y lo indicado en el sistema (outputs 14)
            alg_params16 = {
                'EXPRESSION': "(InconsConc_IdPredial is NULL) or (InconsConc_IdPredial is not NULL and (InconsConc_Incon07 not like '7%' or InconsConc_Incon07 is NULL))",
                'INPUT': outputs14,
                'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs16 = processing.run('native:extractbyexpression', alg_params16)
            outputs16a = outputs16['OUTPUT']
            outputs16b = outputs16['FAIL_OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #SECCIÓN MARCADOS
            #Rehacer campos de los no coincidentes (marcados) del outputs 15 (15b)
            alg_params17 = {
                'FIELDS_MAPPING': [{'expression': '"Identificador"','length': 0,'name': 'Identificador','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Bloque"','length': 0,'name': 'Bloque','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Incon07"','length': 0,'name': 'Inconsistencia07','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Relacion"','length': 0,'name': 'Relacion','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Observacion"','length': 0,'name': 'Observacion','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs15b,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs17 = processing.run('native:refactorfields', alg_params17)
            outputs17 = outputs17['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Rehacer campos de los no coincidentes (marcados) del outputs 16 (16b)
            alg_params18 = {
                'FIELDS_MAPPING': [{'expression': '"Identificador"','length': 0,'name': 'Identificador','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Bloque"','length': 0,'name': 'Bloque','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Incon07"','length': 0,'name': 'Inconsistencia07','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Relacion"','length': 0,'name': 'Relacion','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Observacion"','length': 0,'name': 'Observacion','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs16b,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs18 = processing.run('native:refactorfields', alg_params18)
            outputs18 = outputs18['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Unir capas vectoriales de traslapes marcados outputs 17 y outputs 18
            alg_params19 = {
                'CRS': QgsCoordinateReferenceSystem('EPSG:5367'),
                'LAYERS': [outputs17,outputs18],
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs19 = processing.run('native:mergevectorlayers', alg_params19)
            outputs19 = outputs19['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Quitar campos de la capa final de marcados (outputs 19)
            alg_params20 = {
                'COLUMN': ['layer','path'],
                'INPUT': outputs19,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs20 = processing.run('native:deletecolumn', alg_params20)
            outputs20 = outputs20['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #SECCIÓN NO MARCADOS
            #Rehacer campos de los coincidentes (NO marcados) del outputs 15 (15a)
            alg_params21 = {
                'FIELDS_MAPPING': [{'expression': '"Identificador"','length': 0,'name': 'Identificador','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Bloque"','length': 0,'name': 'Bloque','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Relacion"','length': 0,'name': 'Relacion','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Observacion"','length': 0,'name': 'Observacion','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs15a,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs21 = processing.run('native:refactorfields', alg_params21)
            outputs21 = outputs21['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Rehacer campos de los coincidentes (NO marcados) del outputs 16 (16a)
            alg_params22 = {
                'FIELDS_MAPPING': [{'expression': '"Identificador"','length': 0,'name': 'Identificador','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"Bloque"','length': 0,'name': 'Bloque','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Relacion"','length': 0,'name': 'Relacion','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                                   {'expression': '"InconsConc_Observacion"','length': 0,'name': 'Observacion','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
                'INPUT': outputs16a,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs22 = processing.run('native:refactorfields', alg_params22)
            outputs22 = outputs22['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Unir capas vectoriales de traslapes marcados outputs 21 y outputs 22
            alg_params23 = {
                'CRS': QgsCoordinateReferenceSystem('EPSG:5367'),
                'LAYERS': [outputs21,outputs22],
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs23 = processing.run('native:mergevectorlayers', alg_params23)
            outputs23 = outputs23['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 3
            
            #Quitar campos de la capa final de marcados (outputs 23)
            alg_params24 = {
                'COLUMN': ['layer','path'],
                'INPUT': outputs23,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs24 = processing.run('native:deletecolumn', alg_params24)
            outputs24 = outputs24['OUTPUT']
            barra.setValue(prog_bar)
            prog_bar += 19
            
            #Salidas finales
            outputs20.setName('Traslapes Marcados')
            outputs24.setName('Traslapes No Marcados - Revisar')
            QgsProject.instance().addMapLayer(outputs20)
            QgsProject.instance().addMapLayer(outputs24)
            
            #Eliminar temporales no necesarios
            del outputs0,outputs1,outputs2,outputs3,outputs4,outputs5,
            outputs6,outputs7,outputs8,outputs9,outputs10,outputs11,
            outputs12,outputs13,outputs14,outputs15,outputs16,outputs17,
            outputs18,outputs19,outputs21,outputs22,outputs23
            
            barra.setValue(prog_bar)
            iface.messageBar().clearWidgets()
            iface.messageBar().pushSuccess('Inconsistencia 7', 'Finalizado correctamente')