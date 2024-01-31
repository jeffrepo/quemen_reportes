from odoo import models, fields, api
from collections import defaultdict
import logging
import xlsxwriter
import io
import base64
import dateutil.parser
import datetime
import locale

class VentasAnuales(models.TransientModel):
    _name = 'quemen_reportes.quemen_ventas_anual.wizard'
    _description = "Reporte para pasteleria "

    fecha_inicio = fields.Date('Fecha inicio', required=True)
    fecha_final = fields.Date('Fecha final', required=True)
    categoria_ids = fields.Many2many('product.category','quemen_reportes_categoria_rela', string="Categoria", required=True)
    tienda_ids = fields.Many2many('pos.config','quemen_reporte_ventas_anual_tiendas_rel',string="Tiendas", required=True)
    name = fields.Char('File Name', size=32)
    archivo = fields.Binary('Archivo')
    locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8"))

    def generar_excel(self):
        # Reporte Venta por familia
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            # libro = xlsxwriter.Workbook('borders.xlsx')
            # worksheet = libro.add_worksheet()
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')

            merge_format = libro.add_format({'align': 'center'})

            pedidos = self.env['pos.order'].search([('date_order','>=',str(w.fecha_inicio)),('date_order','<=',str(w.fecha_final))])
            atrasInicio=w.fecha_inicio
            atras=atrasInicio.year-1
            fFechaInicioDM=atrasInicio.strftime('%d,%m')
            añoAtras=fFechaInicioDM+","+str(atras)
            atrasFinal=w.fecha_final
            atras1=atrasFinal.year-1
            fFechaFinalDM=atrasFinal.strftime('%d,%m')
            añoAtrasF=fFechaFinalDM+","+str(atras1)
            pedidosAtras=self.env['pos.order'].search([('date_order','>=',str(añoAtras)),('date_order','<=',str(añoAtrasF))])
            listado_categorias={}
            listado_productos={}
            listado_categoria_padre={}
            categorias_hijas={}
            productos=[]
            productosh=[]
            productosAñoA=[]
            totalImporte=0
            totalImpPdre=0
            ventasTotales=0
            totVtasAñoP=0
            totVtasAñoPdre=0
            totVtasAñoPasadoPadre=0
            cumplidoCategoria=0
            totalPzas=0
            totPzasAñoP=0
            tot=0
            fincremento=0
            totPzasPadr=0
            calculoIncre=0
            incremento=0
            totalMtaPdre=0
            sumaVentas=0
            totalcumplPdre=0
            categoria_hija=0
            totPzasHja=0
            fecha1=w.fecha_final
            fechaFinal=fecha1.strftime('%d,%m,%Y')
            for pedido in pedidos:
                unaFecha=pedido.date_order
                fechaPedido=unaFecha.strftime('%d,%m,%Y')
                añoActual=unaFecha.strftime('%Y')
                if pedido.config_id.id in w.tienda_ids.ids:
                    for lineas in pedido.lines:
                        if lineas.product_id.categ_id.id in w.categoria_ids.ids:
                            if lineas.product_id.categ_id.id not in listado_categorias:
                                metas = self.env['quemen.metas'].search([('fecha','>=',str(w.fecha_inicio)),('fecha','<=',str(w.fecha_final))])
                                # degustacion = self.env['stock.picking'].search([('fecha','>=', str(w.fecha_inicio)),('fecha','<=',str(w.fecha_final))])
                        # Listado categoria padre
                        if lineas.product_id.categ_id.id in w.categoria_ids.ids:
                            if lineas.product_id.categ_id.parent_id.id not in listado_categoria_padre:
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]={
                                'categoria_padre': lineas.product_id.categ_id.parent_id.name,
                                'categorias_hijas':{},
                                'id_padre':lineas.product_id.categ_id.parent_id.id,
                                'totPzasPadr': 0,
                                'totalImpPdre':0,
                                'totalMtaPdre':0,
                                'totalcumplPdre':0,
                                'pzasPadreAñoPasado': 0,
                                'totVtasAñoPdre':0,
                                'totVtasAñoPasadoPadre': 0,
                                'incrementoPadre': 0,
                                'costoTotalPadre': 0,
                                'porcentajeCostoTotalPadre':0,
                                'degustaciones_padre':0,
                                'devolucion_padre':0,
                                'porcentaje_padre': 0}
                            if lineas.product_id.categ_id.id not in listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas']:
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]={
                                'nombre': lineas.product_id.categ_id.name,
                                'productosh':{},
                                'id_hija':0,
                                'totalImporte':0,
                                'metas': 0,
                                'cumplidoCategoria':0,
                                'totalPzas':0,
                                'ventasTotales':0,
                                'totPzasAñoP':0,
                                'totVtasAñoP':0,
                                'incremento':0,
                                'costoTotal':0,
                                'porcentajeCostoTotal': 0,
                                'degustaciones_hijas':0,
                                'devolucion_hija':0,
                                'porcentaje_hija':0}
                                for met in metas:
                                    if met.tienda_almacen_id.id in w.tienda_ids.ids:
                                        for lin in met.linea_ids:
                                            if lin.categoria_id.id == lineas.product_id.categ_id.id:
                                                if lin.categoria_id not in listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas']:
                                                    listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['metas']=round(lin.metaTotal,2)
                                                    listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalMtaPdre']+=round(lin.metaTotal,2)
                                #
                                # for degustaciones in degustacion:
                                #     if
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]={
                            'nombre':lineas.product_id.name,
                            'id_producto':lineas.product_id.id,
                            'piezas': 0,
                            'monto':0,
                            'degustacion':0,
                            'devolucion':0,
                            'porcentaje_devo':0}
                            if fechaPedido == fechaFinal:
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['piezas']+=round(lineas.qty,2)
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['monto']+=round(lineas.price_subtotal_incl,2)
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['totalPzas']+=round(lineas.qty,2)
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['totalImporte']+=round(listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['monto'],2)

                            if listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['metas'] <= 0:
                                print("No hay meta")
                            if listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['metas'] > 0:
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['cumplidoCategoria']=round((listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['totalImporte']/listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['metas'])*100,2)
                            fincremento=lineas.qty*lineas.product_id.standard_price
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['costoTotal']+=round(fincremento,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['ventasTotales']+=round(lineas.price_subtotal_incl,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['porcentajeCostoTotal']=round((listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['costoTotal']/listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['ventasTotales'])*100,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totPzasPadr']+=round(listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['piezas'],2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalImpPdre']+=round(listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['monto'],2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totVtasAñoPdre']+=round(lineas.price_subtotal_incl,2)
                            if listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalMtaPdre'] > 0:
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalcumplPdre']=round((listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalImpPdre']/listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalMtaPdre'])*100,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['costoTotalPadre']+=round(fincremento,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['porcentajeCostoTotalPadre']=round((listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['costoTotalPadre']/listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totVtasAñoPdre'])*100,2)


            incrementoPadre=0
            for pedidosA in pedidosAtras:
                if pedidosA.config_id.id in w.tienda_ids.ids:
                    for lineas1 in pedidosA.lines:
                        if lineas1.product_id.categ_id.parent_id.id in listado_categoria_padre and lineas1.product_id.categ_id.id in listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas']:
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['totPzasAñoP']+=round(lineas1.qty,2)
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['totVtasAñoP']+=round(lineas1.price_subtotal_incl,2)
                            calculoIncre=round((listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['ventasTotales']/(listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['totVtasAñoP']-1))*100,2)
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['incremento']=round(calculoIncre,2)
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['totVtasAñoPasadoPadre']+=lineas1.price_subtotal_incl
                            incrementoPadre=round((listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['totVtasAñoPdre']/(listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['totVtasAñoPasadoPadre']-1))*100,2)
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['incrementoPadre']=round(incrementoPadre,2)
                            # if lineas1.product_id.categ_id.id in listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas']:
                            #     listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['productosh'][lineas1.product_id.id]['piezasAñoPasado']+=lineas1.qty
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['pzasPadreAñoPasado']+= round(lineas1.qty,2)

            tienda = w.tienda_ids

            logging.warn('Listado categoria padre')
            logging.warn(listado_categoria_padre)
            fecha_inicio_hora = ''
            fecha_inicio_hora = str(w.fecha_inicio)+' 00:00:00'
            fecha_final_hora = ''
            fecha_final_hora = str(w.fecha_final)+' 23:59:00'

            operacion_degustaciones=self.env['stock.picking'].search([('picking_type_id','=',tienda.salida_degustacion_id.id),('scheduled_date','>=',str(fecha_inicio_hora)),('scheduled_date','<=',str(fecha_final_hora))])
            # ,('date','>=',str(fecha_inicio_hora)),('date','<=',str(fecha_final_hora))
            degus= 0;
            for degustacion in operacion_degustaciones:
                degustacion_padre=0
                id_padre=0

                for lineas in degustacion.move_line_ids_without_package:
                    if lineas.product_id.categ_id.parent_id.id in listado_categoria_padre and lineas.product_id.categ_id.id in listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas']:
                        degus = lineas.qty_done * lineas.product_id.standard_price;
                        listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['degustacion']=round(degus,2);
                        id_padre =lineas.product_id.categ_id.parent_id.id
                        degustaciones_hija =0
                        degustaciones_hija += round(listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['degustacion'],2)

            operacion_devoluciones=self.env['stock.picking'].search([('picking_type_id','=',tienda.devolucion_producto_id.id),('scheduled_date','>=',str(fecha_inicio_hora)),('scheduled_date','<=',str(fecha_final_hora))])

            devo=0
            for devolucion in operacion_devoluciones:
                for lineas in devolucion.move_line_ids_without_package:
                    if lineas.product_id.categ_id.parent_id.id in listado_categoria_padre and lineas.product_id.categ_id.id in listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas']:
                        devo = lineas.qty_done * lineas.product_id.standard_price
                        listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['devolucion']=round(devo,2);


            for datos_dicc in listado_categoria_padre:
                total_degu_padre = 0
                total_dev_padre = 0
                for datos_dicc_dentro in listado_categoria_padre[datos_dicc]['categorias_hijas']:
                    total_dev_hija = 0
                    total_degu_hija = 0
                    for id_producto in listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['productosh']:
                        total_degu_hija += round(listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['productosh'][id_producto]['degustacion'],2)
                        total_dev_hija += round(listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['productosh'][id_producto]['devolucion'],2)

                    listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['devolucion_hija'] = round(total_dev_hija,2)
                    total_dev_padre += round(listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['devolucion_hija'],2)
                    listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['degustaciones_hijas'] = round(total_degu_hija,2)
                    total_degu_padre += round(listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['degustaciones_hijas'],2)
                    if listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['ventasTotales'] > 0:
                        porcentaje = (listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['devolucion_hija']/listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['ventasTotales'])*100
                        listado_categoria_padre[datos_dicc]['categorias_hijas'][datos_dicc_dentro]['porcentaje_hija'] = round(porcentaje,2)

                listado_categoria_padre[datos_dicc]['devolucion_padre'] = round(total_dev_padre, 2)
                listado_categoria_padre[datos_dicc]['degustaciones_padre'] = round(total_degu_padre, 2)

                if listado_categoria_padre[datos_dicc]['totVtasAñoPdre'] > 0:
                    porcentaje_padre = ( listado_categoria_padre[datos_dicc]['devolucion_padre'] /listado_categoria_padre[datos_dicc]['totVtasAñoPdre'])*100

                listado_categoria_padre[datos_dicc]['porcentaje_padre'] = round(porcentaje_padre, 2)


            logging.warn("nuevo listado ")
            logging.warn(listado_categoria_padre)


            borde = libro.add_format({'border': 2, 'border_color':'#2caad1', 'fg_color': '#067ca1', 'color':'#ffffff'})
            negrita = libro.add_format({'bold': 1, 'fg_color': '#d5d9de'})
            fon_cat_hijas = libro.add_format({'fg_color': '#b8d7ff'})
            hoja.write(2,1, 'LINEA QUEMEN', negrita)
            hoja.write(3,2, 'Venta día ')
            dia=fecha1.strftime('%d')
            hoja.write(3,3, str(dia))
            mes=fecha1.strftime('%b')
            año=fecha1.strftime('%Y')
            hoja.write(3,4, str(mes)+ " " + str(año))

            hoja.write(3,6, 'Acumulado')
            diaI=atrasInicio.strftime('%d')
            hoja.write(3,7, str(diaI))
            hoja.write(3,8, 'al '+ str(dia))
            hoja.write(3,9, str(mes)+" "+str(año))


            hoja.write(4,1, 'Descripción Corta', borde)
            hoja.write(4,2, 'Piezas', borde)
            hoja.write(4,3, 'Importe', borde)
            hoja.write(4,4, 'Meta', borde)
            hoja.write(4,5, '%Cumplido', borde)
            años=fecha1.strftime('%Y')
            hoja.write(4,6, 'Ventas ' +str(años), borde)
            hoja.write(4,7, 'VTA PZAS ' +str(atras1), borde)
            hoja.write(4,8, 'VENTA ' +str(atras1), borde)
            hoja.write(4,9, 'INCREMENTO', borde)
            hoja.write(4,10, 'Costo Total', borde)
            hoja.write(4,11, '% Costo Total', borde)
            hoja.write(4,12, 'DESGUS', borde)
            hoja.write(4,13, 'DEVO', borde)
            hoja.write(4,14, '%DEVO', borde)
            fila1=5
            total_final_piezas =0
            total_final_importe =0
            total_final_meta=0
            total_final_cumplido=0
            total_final_ventas_actual=0
            total_final_piezas_año_pasado=0
            total_final_ventas_año_atras=0
            total_final_incremento=0
            total_final_costo_final=0
            total_final_porcentaje_costo=0
            total_final_degustaciones = 0
            total_final_devoluciones = 0
            for cate in listado_categoria_padre:
                for catehija in listado_categoria_padre[cate]['categorias_hijas']:
                    hoja.write(fila1, 1, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['nombre']), fon_cat_hijas)
                    hoja.write(fila1, 2, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['totalPzas']), fon_cat_hijas)
                    hoja.write(fila1, 3, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['totalImporte']), fon_cat_hijas)
                    hoja.write(fila1, 4, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['metas']), fon_cat_hijas)
                    hoja.write(fila1, 5, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['cumplidoCategoria']), fon_cat_hijas)
                    hoja.write(fila1, 6, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['ventasTotales']), fon_cat_hijas)
                    hoja.write(fila1, 7, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['totPzasAñoP']), fon_cat_hijas)
                    hoja.write(fila1, 8, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['totVtasAñoP']), fon_cat_hijas)
                    hoja.write(fila1, 9, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['incremento']), fon_cat_hijas)
                    hoja.write(fila1, 10, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['costoTotal']), fon_cat_hijas)
                    hoja.write(fila1, 11, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['porcentajeCostoTotal']), fon_cat_hijas)
                    hoja.write(fila1, 12, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['degustaciones_hijas']), fon_cat_hijas)
                    hoja.write(fila1, 13, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['devolucion_hija']), fon_cat_hijas)
                    hoja.write(fila1, 14, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['porcentaje_hija'])+'%', fon_cat_hijas)
                    fila1+=1
                    for prod in listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh']:
                        hoja.write(fila1, 1, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['nombre']))
                        hoja.write(fila1, 2, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['piezas']))
                        hoja.write(fila1, 3, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['monto']))
                        hoja.write(fila1, 12, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['degustacion']))
                        hoja.write(fila1, 13, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['devolucion']))
                        # hoja.write(fila1, 7, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['piezasAñoPasado']))
                        fila1+=1
                hoja.write(fila1, 1, 'SUBTOTAL '+str(listado_categoria_padre[cate]['categoria_padre']), negrita)
                hoja.write(fila1, 2, str(listado_categoria_padre[cate]['totPzasPadr']), negrita)
                total_final_piezas +=round(listado_categoria_padre[cate]['totPzasPadr'],2)
                hoja.write(fila1, 3, str(round(listado_categoria_padre[cate]['totalImpPdre'],2)), negrita)
                total_final_importe += round(listado_categoria_padre[cate]['totalImpPdre'],2)
                hoja.write(fila1, 4, str(round(listado_categoria_padre[cate]['totalMtaPdre'],2)), negrita)
                total_final_meta += round(listado_categoria_padre[cate]['totalMtaPdre'],2)
                hoja.write(fila1, 5, str(round(listado_categoria_padre[cate]['totalcumplPdre'],2)), negrita)
                total_final_cumplido += listado_categoria_padre[cate]['totalcumplPdre']
                hoja.write(fila1, 6, str(round(listado_categoria_padre[cate]['totVtasAñoPdre'],2)), negrita)
                total_final_ventas_actual += round(listado_categoria_padre[cate]['totVtasAñoPdre'],2)
                hoja.write(fila1, 7, str(round(listado_categoria_padre[cate]['pzasPadreAñoPasado'],2)), negrita)
                total_final_piezas_año_pasado += round(listado_categoria_padre[cate]['pzasPadreAñoPasado'],2)
                hoja.write(fila1, 8, str(round(listado_categoria_padre[cate]['totVtasAñoPasadoPadre'],2)), negrita)
                total_final_ventas_año_atras += round(listado_categoria_padre[cate]['totVtasAñoPasadoPadre'],2)
                hoja.write(fila1, 9, str(round(listado_categoria_padre[cate]['incrementoPadre'],2)), negrita)
                total_final_incremento += round(listado_categoria_padre[cate]['incrementoPadre'],2)
                hoja.write(fila1, 10, str(round(listado_categoria_padre[cate]['costoTotalPadre'],2)), negrita)
                total_final_costo_final += round(listado_categoria_padre[cate]['costoTotalPadre'],2)
                hoja.write(fila1, 11, str(round(listado_categoria_padre[cate]['porcentajeCostoTotalPadre'],2)), negrita)
                total_final_porcentaje_costo+=round(listado_categoria_padre[cate]['porcentajeCostoTotalPadre'],2)
                hoja.write(fila1, 12, str(round(listado_categoria_padre[cate]['degustaciones_padre'],2)), negrita)
                total_final_degustaciones += round(listado_categoria_padre[cate]['degustaciones_padre'],2)
                hoja.write(fila1, 13, str(round(listado_categoria_padre[cate]['devolucion_padre'],2)), negrita)
                total_final_devoluciones +=round(listado_categoria_padre[cate]['devolucion_padre'],2)
                hoja.write(fila1, 14, str(round(listado_categoria_padre[cate]['porcentaje_padre'],2))+'%', negrita)
                fila1+=1

        negrita = libro.add_format({'bold': 1, 'fg_color': '#5a98bf', 'color':'#ffffff'})
        porcentaje_final = round((total_final_devoluciones/total_final_ventas_actual)*100,2)
        hoja.write(fila1, 1, 'TOTAL', negrita)
        hoja.write(fila1, 2, str(total_final_piezas), negrita)
        hoja.write(fila1, 3, str(total_final_importe), negrita)
        hoja.write(fila1, 4, str(total_final_meta), negrita)
        hoja.write(fila1, 5, str(total_final_cumplido), negrita)
        hoja.write(fila1, 6, str(total_final_ventas_actual), negrita)
        hoja.write(fila1, 7, str(total_final_piezas_año_pasado), negrita)
        hoja.write(fila1, 8, str(total_final_ventas_año_atras), negrita)
        hoja.write(fila1, 9, str(total_final_incremento), negrita)
        hoja.write(fila1, 10, str(total_final_costo_final), negrita)
        hoja.write(fila1, 11, str(total_final_porcentaje_costo), negrita)
        hoja.write(fila1, 12, str(total_final_degustaciones), negrita)
        hoja.write(fila1, 13, str(total_final_devoluciones), negrita)
        hoja.write(fila1, 14, str(porcentaje_final)+'%', negrita)
        libro.close()
        datos = base64.b64encode(f.getvalue())
        self.write({'archivo': datos, 'name':'Reporte.xls'})

        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'quemen_reportes.quemen_ventas_anual.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }



    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['fecha_inicio','fecha_final'])
        res = res and res[0] or {}
        datas['form'] = res
        # datas['form'] = False
        return self.env.ref('quemen_reportes.quemen_ventas_anual.wizard').report_action([], data=datas)
