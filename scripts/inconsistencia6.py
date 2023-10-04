'''

Diquís
Complemento para labores internas en Telespazio Costa Rica.

Archivo de la clase Inconsistencia 6 y sus herramientas.

Autor: Andrés David Chavarría-Palma
Colabora: Jason Alberto Navarro Ulate, Jorge Daniel García Girón

Marzo - 2023

'''
import processing
from qgis.core import QgsMapLayerProxyModel, QgsProcessing, QgsProject, QgsCoordinateReferenceSystem
from qgis.utils import iface
from PyQt5.QtWidgets import QProgressBar
from .inconsistencia6_ui import incon6UI

class Inconsistencia6:
   inc6 = incon6UI()
   def activarBoton(self):
        if (len(Inconsistencia6.inc6.bloque.text()) == 8 or len(Inconsistencia6.inc6.bloque.text()) == 5) and Inconsistencia6.inc6.bloque.text().isdigit():
            Inconsistencia6.inc6.button_box.setEnabled(True)
        else:
            Inconsistencia6.inc6.button_box.setEnabled(False)

   def tools(self):
        Inconsistencia6.inc6.mc.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        Inconsistencia6.inc6.ic.setFilters(QgsMapLayerProxyModel.NoGeometry)
        Inconsistencia6.inc6.traslapes.setFilters(QgsMapLayerProxyModel.NoGeometry)
        Inconsistencia6.inc6.seg.setFilters(QgsMapLayerProxyModel.NoGeometry)
        Inconsistencia6.inc6.fm.setFilters(QgsMapLayerProxyModel.NoGeometry)

        Inconsistencia6.inc6.bloque.textChanged.connect(Inconsistencia6.activarBoton)
            
        Inconsistencia6.inc6.show()
        result = Inconsistencia6.inc6.exec_()
        if result:
            #Barra de progreso
            barra_mensaje = iface.messageBar().createMessage('En proceso...')
            barra = QProgressBar()
            barra.setMaximum(100)
            barra_mensaje.layout().addWidget(barra)
            iface.messageBar().pushWidget(barra_mensaje)

            #Variables de entrada.
            txt_codigo = Inconsistencia6.inc6.bloque.text()
            mosai_catas = Inconsistencia6.inc6.mc.currentLayer()
            incon_conci = Inconsistencia6.inc6.ic.currentLayer()
            traslapes = Inconsistencia6.inc6.traslapes.currentLayer()
            segregaciones = Inconsistencia6.inc6.seg.currentLayer()
            filial_matriz = Inconsistencia6.inc6.fm.currentLayer()
            prog_bar = 5

            barra.setValue(prog_bar)
            prog_bar += 5

            #Extraer datos de traslapes por distrito.
            if len(txt_codigo) == 5:
                expres_alg_params0 = f"Traslapes_ParejaBloque like trim('{txt_codigo}') || '%'"
            else:
                expres_alg_params0 = f"Traslapes_ParejaBloque like substr('{txt_codigo}',1,5) || '%'"

            alg_params0 = {'EXPRESSION': expres_alg_params0,
                            'INPUT': traslapes,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs0 = processing.run('native:extractbyexpression', alg_params0)
            outputs0 = outputs0['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            #Extraer por expresión. Se extrae los datos de todo el distrito concierniente al bloque elegido.
            if len(txt_codigo) == 5:
                expres_alg_params1 = f"bloque like trim('{txt_codigo}') || '%'"
            else:
                expres_alg_params1 = f"bloque like substr('{txt_codigo}',1,5) || '%'"

            alg_params1 = {'EXPRESSION': expres_alg_params1,
                            'INPUT': mosai_catas,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs1 = processing.run('native:extractbyexpression', alg_params1)
            outputs1 = outputs1['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            #Buffer negativo
            alg_params2 = {'DISSOLVE': False,
                            'DISTANCE': -0.425,
                            'END_CAP_STYLE': 2,  # Cuadrado
                            'INPUT': outputs1,
                            'JOIN_STYLE': 1,  # Inglete
                            'MITER_LIMIT': 2,
                            'SEGMENTS': 5,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs2 = processing.run('native:buffer', alg_params2)
            outputs2 = outputs2['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            #Intersección
            alg_params3 = {'INPUT': outputs2,
                            'OVERLAY': outputs2,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs3 = processing.run('native:intersection', alg_params3)
            outputs3 = outputs3['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            # Extraer por expresión. Filtrar el resultado de intersección para visualizar únicamente las intersecciones reales.
            alg_params4 = {'EXPRESSION': '"identificador" != "identificador_2"',
                            'INPUT': outputs3,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs4 = processing.run('native:extractbyexpression', alg_params4)
            outputs4 = outputs4['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            # Rehacer campos. Limpia y ordena la tabla de atributos de la intersección.
            alg_params5 = {'FIELDS_MAPPING': [{'expression': "identificador || '-' || identificador_2",'length': 0,'name': 'Pareja','precision': 0,'type': 10},
                                                {'expression': 'identificador','length': 0,'name': 'Identificador_A','precision': 0,'type': 10},
                                                {'expression': 'identificador_2','length': 0,'name': 'Identificador_B','precision': 0,'type': 10},
                                                {'expression': 'bloque','length': 0,'name': 'Bloque_A','precision': 0,'type': 10},
                                                {'expression': 'bloque_2','length': 0,'name': 'Bloque_B','precision': 0,'type': 10}],
                            'INPUT': outputs4,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs5 = processing.run('native:refactorfields', alg_params5)
            outputs5 = outputs5['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            if len(txt_codigo) == 8:
                # Capa final de traslapes espaciales detectados en la base de datos Postgres/Postgis.
                # Aplica solo para cuando el usuario ingresa código de bloque.
                alg_params6 = {'EXPRESSION': f"Bloque_A like '{txt_codigo}' or Bloque_B like '{txt_codigo}'",
                                'INPUT': outputs5,
                                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
                outputs6 = processing.run('native:extractbyexpression', alg_params6)
                outputs6 = outputs6['OUTPUT']
            else:
                outputs6 = outputs5

            barra.setValue(prog_bar)
            prog_bar += 5

            # Unión entre los traslape espaciales y la tabla InconsistenciasConciliación
            # para verificar aquellos traslapes no marcado en el sistema y que deberían revisarse.
            alg_params7 = {'DISCARD_NONMATCHING': True,
                            'FIELD': 'Identificador_A',
                            'FIELD_2': 'InconsConc_IdPredial',
                            'INPUT': outputs6,
                            'INPUT_2': incon_conci,
                            'METHOD': 1,  # Tomar solo los atributos del primer objeto coincidente (uno a uno)
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs7 = processing.run('native:joinattributestable', alg_params7)
            outputs7 = outputs7['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            #Filtra y separa los predios como marcados y no marcados entre lo espacial y lo indicado en el sistema.
            alg_params8 = {'EXPRESSION': "(InconsConc_IdPredial is NULL) or (InconsConc_IdPredial is not NULL and (InconsConc_Incon06 not like '6%' or InconsConc_Incon06 is NULL))",
                            'INPUT': outputs7,
                            'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs8 = processing.run('native:extractbyexpression', alg_params8)
            outputs8a = outputs8['OUTPUT']
            outputs8b = outputs8['FAIL_OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            # Rehacer campos para los traslapes NO MARCADOS.
            alg_params9 = {'FIELDS_MAPPING': [{'expression': '"Pareja"','length': 0,'name': 'Pareja','precision': 0,'type': 10},
                                                {'expression': '"Identificador_A"','length': 0,'name': 'Identificador_A','precision': 0,'type': 10},
                                                {'expression': '"Identificador_B"','length': 0,'name': 'Identificador_B','precision': 0,'type': 10},
                                                {'expression': '"Bloque_A"','length': 0,'name': 'Bloque_A','precision': 0,'type': 10},
                                                {'expression': '"Bloque_B"','length': 0,'name': 'Bloque_B','precision': 0,'type': 10},
                                                {'expression': '"InconsConc_Relacion"','length': 0,'name': 'Relacion','precision': 0,'type': 10},
                                                {'expression': '"InconsConc_Observacion"','length': 0,'name': 'Observacion','precision': 0,'type': 10}],
                            'INPUT': outputs8a,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs9 = processing.run('native:refactorfields', alg_params9)
            outputs9 = outputs9['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            # SECCIÓN MARCADOS
            # Rehacer campos marcados
            alg_params10 = {'FIELDS_MAPPING': [{'expression': '"Pareja"','length': 0,'name': 'Pareja','precision': 0,'type': 10},
                                                {'expression': '"Identificador_A"','length': 0,'name': 'Identificador_A','precision': 0,'type': 10},
                                                {'expression': '"Identificador_B"','length': 0,'name': 'Identificador_B','precision': 0,'type': 10},
                                                {'expression': '"Bloque_A"','length': 0,'name': 'Bloque_A','precision': 0,'type': 10},
                                                {'expression': '"Bloque_B"','length': 0,'name': 'Bloque_B','precision': 0,'type': 10},
                                                {'expression': '"InconsConc_Relacion"','length': 0,'name': 'Relacion','precision': 0,'type': 10},
                                                {'expression': '"InconsConc_Observacion"','length': 0,'name': 'Observacion','precision': 0,'type': 10}],
                            'INPUT': outputs8b,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs10 = processing.run('native:refactorfields', alg_params10)
            outputs10 = outputs10['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            #Rehacer campos de la tabla Traslapes.
            alg_params11 = {'FIELDS_MAPPING': [{'expression': "Traslapes_ParejaId || '-' || Traslapes_IdPredial",'length': 0,'name': 'Pareja','precision': 0,'type': 10},
                                                {'expression': '"Traslapes_ParejaBloque"','length': 0,'name': 'Bloque_A','precision': 0,'type': 10},
                                                {'expression': '"Traslapes_ParejaId"','length': 0,'name': 'Identificador_A','precision': 0,'type': 10},
                                                {'expression': '"Traslapes_IdPredial"','length': 0,'name': 'Identificador_B','precision': 0,'type': 10},
                                                {'expression': '"Traslapes_Codigo"','length': 0,'name': 'Codigo','precision': 0,'type': 10}],
                            'INPUT': outputs0,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs11 = processing.run('native:refactorfields', alg_params11)
            outputs11 = outputs11['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            # Segunda verificación si los marcados en el sistema realmente tienen marcados los traslapes
            # en la respectiva tabla.
            alg_params12 = {'DISCARD_NONMATCHING': True,
                                'FIELD': 'Pareja',
                                'FIELD_2': 'Pareja',
                                'INPUT': outputs10,
                                'INPUT_2': outputs11,
                                'METHOD': 0,  # Crear objeto separado para cada objeto coincidente (uno a muchos)
                                'NON_MATCHING': QgsProcessing.TEMPORARY_OUTPUT,
                                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs12 = processing.run('native:joinattributestable', alg_params12)
            outputs12a = outputs12['OUTPUT']
            outputs12b = outputs12['NON_MATCHING']

            barra.setValue(prog_bar)
            prog_bar += 5

            # Quitar campos sobrantes en Traslapes Marcados
            alg_params13 = {'COLUMN': ['Pareja_2','Bloque_A_2','Identificador_A_2','Identificador_B_2'],
                            'INPUT': outputs12a,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs13 = processing.run('native:deletecolumn', alg_params13)
            outputs13 = outputs13['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 5

            # SECCIÓN NO MARCADOS
            # Combina la tabla de No marcados en InconsistenciaConciliación (Output 9)
            # y la tabla de No marcardos en Traslapes (Output 12b)
            alg_params14 = {'CRS': QgsCoordinateReferenceSystem('EPSG:5367'),
                            'LAYERS': [outputs12b,outputs9],
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs14 = processing.run('native:mergevectorlayers', alg_params14)
            outputs14 = outputs14['OUTPUT']

            barra.setValue(prog_bar)
            prog_bar += 15

            # Quitar campos sobrantes en Traslapes No Marcados.
            alg_params15 = {'COLUMN': ['path','layer'],
                            'INPUT': outputs14,
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
            outputs15 = processing.run('native:deletecolumn', alg_params15)
            outputs15 = outputs15['OUTPUT']
            
            outputs15.selectByExpression(f"array_contains(aggregate('{segregaciones.name()}','array_agg',a_b), Pareja) or array_contains(aggregate('{segregaciones.name()}','array_agg',b_a), Pareja)")
            outputs15.startEditing()
            outputs15.deleteSelectedFeatures()
            outputs15.commitChanges()

            outputs15.selectByExpression(f"array_contains(aggregate('{filial_matriz.name()}','array_agg',a_b), Pareja) or array_contains(aggregate('{filial_matriz.name()}','array_agg',b_a), Pareja)")
            outputs15.startEditing()
            outputs15.deleteSelectedFeatures()
            outputs15.commitChanges()

            outputs13.setName('Traslapes Marcados')
            outputs15.setName('Traslapes No Marcados')
            QgsProject.instance().addMapLayer(outputs13)
            QgsProject.instance().addMapLayer(outputs15)

            del outputs0,outputs1,outputs2,outputs3,outputs4,outputs5,
            outputs6,outputs7,outputs8a,outputs8b,outputs9,outputs10,
            outputs11,outputs12a,outputs12b,outputs14

            barra.setValue(prog_bar)
            iface.messageBar().clearWidgets()
            iface.messageBar().pushSuccess('Inconsistencia 6', 'Finalizado correctamente')
