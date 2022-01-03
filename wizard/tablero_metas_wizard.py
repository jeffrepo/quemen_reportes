# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict
import logging
import xlsxwriter
import io
import base64
import dateutil.parser
import datetime
from datetime import date
import dateutil.parser
import pytz

class TableroWizard(models.TransientModel):
    _name = 'quemen_reportes.tablero_metas.wizard'
    _description = "Reporte de tablero metas"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_final = fields.Date('Fecha final')
    tienda_ids = fields.Many2many('pos.config','quemen_tiendas_rel',string="Tiendas", required=True)

    archivo = fields.Binary('Archivo')
    name = fields.Char('File Name', size=32)

    def generando_excel (self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')
            total_pedido_tienda = 0
            total_meta_tienda = 0
            cumplimiento = 0
            cumplimiento_acumulado=0
            ventas_rango = 0
            ventas_rango_tienda=0
            metas_rango = 0
            metas_rango_tienda = 0
            total_rango_atras_tienda = 0
            crecimiento = 0
            total_pedidos = 0
            suma_total_productos = 0
            suma_total_productos1 =0
            for tienda in w.tienda_ids:
                # Fecha inicio = Fecha final para la primera parte de "Venta del día"
                busqueda_ventas1 = self.busqueda_ventas(tienda, w.fecha_final, w.fecha_final)
                busqueda_meta1 = self.busqueda_metas(tienda, w.fecha_final, w.fecha_final)
                total_pedido_tienda += busqueda_ventas1
                total_meta_tienda += busqueda_meta1

                # Calculos para rango de ventas Fecha_inico = fecha_inicio y Fecha final = fecha_final
                ventas_rango = self.busqueda_ventas(tienda, w.fecha_inicio, w.fecha_final)
                ventas_rango_tienda += round(ventas_rango,2)
                metas_rango = self.busqueda_metas(tienda, w.fecha_inicio, w.fecha_final)
                metas_rango_tienda += round(metas_rango,2)
                año_actual_inicio = w.fecha_inicio.strftime('%Y')
                año_actual_final = w.fecha_inicio.strftime('%Y')
                menos_año_inicio = int(año_actual_inicio)-1
                menos_año_final = int(año_actual_final)-1
                mes_dia_atras_inicio = w.fecha_inicio.strftime('%m-%d')
                fecha_inicio_año_atras = str(menos_año_inicio)+'-'+mes_dia_atras_inicio
                mes_dia_atras_final = w.fecha_final.strftime('%m-%d')
                fecha_final_año_atras = str(menos_año_final)+'-'+mes_dia_atras_inicio
                ventas_rango_año_atras = self.busqueda_ventas(tienda, fecha_inicio_año_atras, fecha_final_año_atras)
                total_rango_atras_tienda += round(ventas_rango_año_atras,2)

                # Calculo para area de devoluciones y degustaciones

                if tienda.salida_degustacion_id:
                    salida_degustacion = tienda.salida_degustacion_id.id
                    fecha_inicio_hora = ' '
                    fecha_inicio_hora = str(w.fecha_inicio)+' 00:00:00'
                    fecha_final_hora = ' '
                    fecha_final_hora = str(w.fecha_final)+' 23:59:59'

                    salidas_degustaciones=self.env['stock.picking'].search([('picking_type_id','=',salida_degustacion),('scheduled_date','>=',str(fecha_inicio_hora)),('scheduled_date','<=',str(fecha_final_hora))])

                    for salida_degustacion in salidas_degustaciones:
                        precio_coste = 0
                        cantidad_producto = 0
                        total_producto = 0
                        for lineas in salida_degustacion.move_line_ids_without_package:
                            if lineas.product_id.categ_id.parent_id.id != False:
                                precio_coste = lineas.product_id.standard_price
                                cantidad_producto = lineas.qty_done
                                total_producto = (precio_coste * cantidad_producto)

                        suma_total_productos += total_producto

                    id_salida_devolucion = tienda.devolucion_producto_id.id
                    salidas_devoluciones = self.env['stock.picking'].search([('picking_type_id','=',id_salida_devolucion),('scheduled_date','>=',str(fecha_inicio_hora)),('scheduled_date','<=',str(fecha_final_hora))])

                    for salida_devolucion in salidas_devoluciones:
                        precio_coste1 = 0
                        cantidad_producto1 = 0
                        total_producto1 = 0
                        for lineas_devolucion in salida_devolucion.move_line_ids_without_package:
                            if lineas_devolucion.product_id.categ_id.parent_id.id != False:
                                precio_coste1 = lineas_devolucion.product_id.standard_price
                                cantidad_producto1 = lineas_devolucion.qty_done
                                total_producto1 = (precio_coste1 * cantidad_producto1)
                        suma_total_productos1 += total_producto1

                    #Pedidos conforme a las tiendas

                    pedidos = self.env['pos.order'].search([('session_id.config_id','=',tienda.id),('date_order','>=',str(fecha_inicio_hora)),('date_order','<=',str(fecha_final_hora))])

                    for pedido in pedidos:
                        for lineas_pedido in pedido.lines:
                            if lineas_pedido.product_id.categ_id.parent_id.id != False:
                                logging.warn(pedido.name +' '+str(lineas_pedido.price_subtotal_incl))
                                total_pedidos += round(lineas_pedido.price_subtotal_incl,2)
                    # self.order.devolucion_acumulado(salida_degustacion, fecha_inicio_hora, fecha_final_hora)

            logging.warn("total_pedidos")
            logging.warn(total_pedidos)

            ideal_pedidos_degustacion = round((total_pedidos* 0.02),2)
            ideal_pedidos_devolucion = round((total_pedidos * 0.0010),2)
            diferencia = round((total_pedido_tienda - total_meta_tienda),2)
            diferencia_rango = round((ventas_rango_tienda - metas_rango_tienda),2)

            if suma_total_productos1>0:
                porcentaje_real_devo = round((total_pedidos/suma_total_productos1),2)
            if suma_total_productos>0:
                porcentaje_real_degustaciones = round((total_pedidos/suma_total_productos),2)

            logging.warn("porcentaje_real_devo: "+str(porcentaje_real_devo))

            if total_meta_tienda > 0:
                cumplimiento = round( ((total_pedido_tienda/total_meta_tienda)*100) ,2)

            if ventas_rango_tienda > 0:
                cumplimiento_acumulado = round(((ventas_rango_tienda/metas_rango_tienda)*100),2)

            if total_rango_atras_tienda > 0:
                crecimiento = round((((ventas_rango_tienda-total_rango_atras_tienda)/total_rango_atras_tienda)*100),2)

            formato_titulo = libro.add_format({'size': 17, 'color':'#000000', 'align':'center', 'fg_color': '#fcf89f'})
            # libro.add_format({'border': 2, 'size': 20,'border_color':'#2caad1', 'fg_color': '#067ca1', 'color':'#ffffff','align': 'center'})
            hoja.merge_range('B3:C3', 'Reporte Diario ', formato_titulo)

            formato_correcto_fecha = w.fecha_final.strftime('%d/%m/%Y')
            año_actual = w.fecha_final.strftime('%Y')
            año_atras = (int(año_actual) - 1)
            formato_correcto_fecha_inicio = w.fecha_inicio.strftime('%d')
            formato2 = libro.add_format({'size': 12, 'color':'#000000','align':'left', 'fg_color': '#ffbb00', 'border_color':'#ffffff', 'border': 2,})
            formato2_center = libro.add_format({'size': 12, 'color':'#000000','align':'center', 'fg_color': '#ffbb00', 'border_color':'#ffffff', 'border': 2,})
            formato3 = libro.add_format({'color':'#000000','align':'left', 'fg_color': '#d6d4ce', 'border_color':'#ffffff', 'border': 2,})
            formato_cumplimiento_total = libro.add_format({ 'color':'#000000','align':'right', 'fg_color': '#ffbb00', 'border_color':'#ffffff', 'border': 2,})

            totales_grises = libro.add_format({'color':'#000000','align':'right', 'fg_color': '#d6d4ce', 'border_color':'#ffffff', 'border': 2,})
            totales_diferencias = libro.add_format({'color':'#ff0000','align':'right', 'border_color':'#ffffff', 'border': 2,})
            hoja.merge_range('B4:C4', str(formato_correcto_fecha), formato2_center)
            hoja.write(4,1, 'Venta del día ', formato3)
            hoja.write(4,2, str(total_pedido_tienda), totales_grises)
            hoja.write(5,1, 'Meta del día', formato3)
            hoja.write(5,2, str(total_meta_tienda), totales_grises)
            formato_diferencia = libro.add_format({'color':'#000000','align':'left', 'fg_color': '#ff870f', 'border_color':'#ffffff', 'border': 2,})
            hoja.write(6,1, 'Diferencia ', formato_diferencia)
            hoja.write(6,2, str(diferencia), totales_diferencias)
            hoja.write(7,1, 'Cumplimiento ', formato2)
            hoja.write(7,2, str(cumplimiento)+'%', formato_cumplimiento_total)
            fondo_celeste = libro.add_format({'color':'#000000','align':'center', 'fg_color': '#a1e0ff', 'border_color':'#ffffff', 'border': 2,})
            hoja.merge_range('B10:C10', 'Venta acumulada ' +str(formato_correcto_fecha_inicio)+' al '+str(formato_correcto_fecha), fondo_celeste)
            hoja.write(10,1, 'Meta acumulada '+str(año_actual), formato3)
            hoja.write(10,2, str(metas_rango_tienda), totales_grises)
            hoja.write(11,1, 'Venta acumulada '+str(año_actual), formato3)
            hoja.write(11,2, str(ventas_rango_tienda), totales_grises)
            hoja.write(12,1, 'Diferencia', formato_diferencia)
            hoja.write(12,2, str(diferencia_rango), totales_diferencias)
            hoja.write(13,1, 'Venta acumulada '+str(año_atras), formato3)
            hoja.write(13,2, str(total_rango_atras_tienda), totales_diferencias)
            hoja.write(14,1, 'Crecimiento ', formato3)
            hoja.write(14,2, str(crecimiento), totales_grises)
            hoja.write(15,1, 'Cumplimiento acumulado ', formato2)
            hoja.write(15,2, str(cumplimiento_acumulado)+'%', formato_cumplimiento_total)
            

            # Tamaño de las columnas y Tamaño de las filas
            hoja.set_column('B:B', 30)
            hoja.set_column('C:C', 15)
            hoja.set_column('D:D', 15)
            hoja.set_column('E:E', 15)
            hoja.set_row (2, 30)

            hoja.merge_range('B18:C18', 'Devolución y degustación acumulado ', formato3)
            hoja.write(18,1, ' % ', formato2)
            hoja.write(18,2, ' Ideal ', formato2)
            hoja.write(18,3, ' Real ', formato2)
            hoja.write(18,4, ' Diferencia ', formato2)
            hoja.write(19,1, 'Devolución ', formato3)
            hoja.write(19,2, '2.00%', totales_grises)
            hoja.write(19,3, str(porcentaje_real_devo)+'%', totales_grises)
            diferencia_devolucion_porcentaje = round((2-porcentaje_real_devo),2)
            hoja.write(19,4, str(diferencia_devolucion_porcentaje)+'%', totales_diferencias)
            hoja.write(20,1, 'Degustación ', formato3)
            hoja.write(20,2, '0.10%', totales_grises)
            hoja.write(20,3, str(porcentaje_real_degustaciones)+'%', totales_grises)
            diferencia_degustacion_porcentaje = round((0.10-porcentaje_real_degustaciones),2)
            hoja.write(20,4, str(diferencia_degustacion_porcentaje)+'%', totales_diferencias)
            hoja.write(21,1, 'Total ', fondo_celeste)
            fondo_celeste_total = libro.add_format({'color':'#000000','align':'right', 'fg_color': '#a1e0ff', 'border_color':'#ffffff', 'border': 2,})
            hoja.write(21,2, '2.10%', fondo_celeste_total)
            total_columna_real = round((porcentaje_real_devo+porcentaje_real_degustaciones),2)
            hoja.write(21,3, str(total_columna_real)+'%', fondo_celeste_total)
            total_columna_diferencia_porcentaje = round((diferencia_devolucion_porcentaje+diferencia_degustacion_porcentaje),2)
            hoja.write(21,4, str(total_columna_diferencia_porcentaje)+'%', fondo_celeste_total)

            hoja.merge_range('B24:C24', 'Devolución y degustación acumulado ', formato3)
            hoja.write(24,1, ' $ ', formato2)
            hoja.write(24,2, ' Ideal ', formato2)
            hoja.write(24,3, ' Real ', formato2)
            hoja.write(24,4, ' Diferencia ', formato2)
            hoja.write(25,1, 'Devolución ', formato3)
            hoja.write(25,2, '$ '+str(ideal_pedidos_devolucion), totales_grises)
            hoja.write(25,3, '$ '+str(suma_total_productos1), totales_grises)
            diferencia_devolucion_precio = round((ideal_pedidos_devolucion-suma_total_productos1),2)
            hoja.write(25,4, '$ '+str(diferencia_devolucion_precio), totales_diferencias)
            hoja.write(26,1, 'Degustación ', formato3)
            hoja.write(26,2, '$ '+str(ideal_pedidos_degustacion), totales_grises)
            hoja.write(26,3, '$ '+str(suma_total_productos), totales_grises)
            diferencia_degustacion_precio = round((ideal_pedidos_degustacion-suma_total_productos),2)
            hoja.write(26,4, '$ '+str(diferencia_degustacion_precio), totales_diferencias)
            hoja.write(27,1, 'Total ', fondo_celeste)
            total_columna_ideal_monetaria = round((ideal_pedidos_devolucion+ ideal_pedidos_degustacion),2)
            hoja.write(27,2, '$ '+str(total_columna_ideal_monetaria), fondo_celeste_total)
            total_columna_real_monetaria = round((suma_total_productos1+ suma_total_productos),2)
            hoja.write(27,3, '$ '+str(total_columna_real_monetaria), fondo_celeste_total)
            total_columna_diferencia_monetaria =round((diferencia_degustacion_precio+diferencia_devolucion_precio),2)
            hoja.write(27,4, '$ '+str(total_columna_diferencia_monetaria), fondo_celeste_total)
            hoja.merge_range('B30:C30', 'Stock Pastel ¿¿Fecha?? ', formato2)
            hoja.write(30,1, ' Existencia Inicial ', formato3)
            hoja.write(31,1, ' Producción día ', formato3)
            hoja.write(32,1, ' Total Stock ', formato2)

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'Reporte_tablero_metas.xls'})

        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'quemen_reportes.tablero_metas.wizard',
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
        return self.env.ref('quemen_reportes.quemen_tablero_metas.wizard').report_action([], data=datas)

    def busqueda_ventas(self, tienda, fecha_inicio, fecha_final):
        fecha_inicio_hora = ' '
        fecha_inicio_hora = str(fecha_inicio)+' 00:00:00'
        fecha_final_hora = ' '
        fecha_final_hora = str(fecha_final)+' 23:59:59'
        pedidos = self.env['pos.order'].search([('session_id.config_id','=',tienda.id),('date_order','>=',str(fecha_inicio_hora)),('date_order','<=',str(fecha_final_hora))])
        total_pedido=0
        for pedido in pedidos:
            total_pedido+=pedido.amount_total

        return total_pedido

    def busqueda_metas(self, tienda, fecha_inicio, fecha_final):
        fecha_inicio_hora = ' '
        fecha_inicio_hora = str(fecha_inicio)+' 00:00:00'
        fecha_final_hora = ' '
        fecha_final_hora = str(fecha_final)+' 23:59:59'
        metas = self.env['quemen.metas'].search([('tienda_almacen_id','=',tienda.id),('fecha_inicio','>=',str(fecha_inicio_hora)),('fecha_final','<=',str(fecha_final_hora))])
        total_pedido=0
        total_metas=0
        for meta in metas:
            total_linea = 0
            for lineas_meta in meta.linea_ids:
                total_linea += round(lineas_meta.metaTotal,2)

            total_metas += total_linea
        return total_metas
