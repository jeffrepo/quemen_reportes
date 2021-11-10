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

class FamiliaWizard(models.TransientModel):
    _name = 'quemen_reportes.devolucion_familia.wizard'
    _description = "Reporte para pasteleria sobre devoluciones"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_final = fields.Date('Fecha final')
    tienda_ids = fields.Many2many('pos.config','quemen_reporte_familia_degustaciones_rel',string="Tiendas", required=True)
    categoria_ids = fields.Many2many('product.category','quemen_reportes_devo_categoria_rela',string="Categoria")
    archivo = fields.Binary('Archivo')
    name = fields.Char('File Name', size=32)

    def generando_excel (self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')
            diccionario_degustacion_devolucion = {}
            fecha_inicio_hora = ' '
            fecha_inicio_hora = str(w.fecha_inicio)+' 00:00:00'
            fecha_final_hora = ' '
            fecha_final_hora = str(w.fecha_final)+' 23:59:59'

            salida_degustacion = 0
            for id_operacion in w.tienda_ids:
                salida_degustacion = id_operacion.salida_degustacion_id.id
                devolucion = id_operacion.devolucion_producto_id.id
                salidas_degustaciones=self.env['stock.picking'].search([('picking_type_id','=',salida_degustacion),('scheduled_date','>=',str(fecha_inicio_hora)),('scheduled_date','<=',str(fecha_final_hora))])
                devoluciones = self.env['stock.picking'].search([('picking_type_id','=',devolucion),('scheduled_date','>=',str(fecha_inicio_hora)),('scheduled_date','<=',str(fecha_final_hora))])

                for cada_degustacion in salidas_degustaciones:
                    for lineas in cada_degustacion.move_line_ids_without_package:
                        cantidad=0
                        for categoria in w.categoria_ids:
                            if lineas.product_id.categ_id.id == categoria.id and lineas.product_id.categ_id.parent_id.id != False:
                                if lineas.product_id.categ_id.id not in diccionario_degustacion_devolucion:
                                    diccionario_degustacion_devolucion[lineas.product_id.categ_id.id]={
                                    'nombre_categoria_hija_degustacion': lineas.product_id.categ_id.name,
                                    'productos_hijos':{},
                                    'degustacion':0,
                                    'devolucion':0,
                                    'porcentaje_devo':0,
                                    'porcentaje_part_familia':0,
                                    'ideal_dev':2,
                                    'imp_dev_ideal':0,
                                    'dif_dev_ideal':0,
                                    'estado':False,
                                    'importe_pedido':0,
                                    }

                                if lineas.product_id.id not in diccionario_degustacion_devolucion[lineas.product_id.categ_id.id]['productos_hijos']:
                                    diccionario_degustacion_devolucion[lineas.product_id.categ_id.id]['productos_hijos'][lineas.product_id.id]={
                                    'nombre_producto':lineas.product_id.name,
                                    'cantidad':0,
                                    'cantidad_devolucion':0,
                                    'precio_coste':lineas.product_id.standard_price,
                                    'total_cantidad_precio':0,
                                    'total_cantidad_precio_devo':0,
                                    'total_prod_fecha_final':0,
                                    'total_producto_venta':0,
                                    }
                        if lineas.product_id.categ_id.id in diccionario_degustacion_devolucion and lineas.product_id.id in diccionario_degustacion_devolucion[lineas.product_id.categ_id.id]['productos_hijos']:
                            cantidad += lineas.qty_done
                            diccionario_degustacion_devolucion[lineas.product_id.categ_id.id]['productos_hijos'][lineas.product_id.id]['cantidad']+=cantidad
                            diccionario_degustacion_devolucion[lineas.product_id.categ_id.id]['productos_hijos'][lineas.product_id.id]['total_cantidad_precio'] = round((diccionario_degustacion_devolucion[lineas.product_id.categ_id.id]['productos_hijos'][lineas.product_id.id]['cantidad']*diccionario_degustacion_devolucion[lineas.product_id.categ_id.id]['productos_hijos'][lineas.product_id.id]['precio_coste']),2)

                # Verificacion de operaciones tipo devoluciones

                for cada_devolucion in devoluciones:
                    for lineas_devo in cada_devolucion.move_line_ids_without_package:
                        cantidad=0
                        for categoria in w.categoria_ids:
                            if lineas_devo.product_id.categ_id.id == categoria.id and lineas_devo.product_id.categ_id.parent_id.id != False:
                                if lineas_devo.product_id.categ_id.id not in diccionario_degustacion_devolucion:
                                    diccionario_degustacion_devolucion[lineas_devo.product_id.categ_id.id]={
                                    'nombre_categoria_hija_degustacion': lineas_devo.product_id.categ_id.name,
                                    'productos_hijos':{},
                                    'degustacion':0,
                                    'devolucion':0,
                                    'porcentaje_devo':0,
                                    'porcentaje_part_familia':0,
                                    'ideal_dev':2,
                                    'imp_dev_ideal':0,
                                    'dif_dev_ideal':0,
                                    'estado':False,
                                    'importe_pedido':0,
                                    }
                                if lineas_devo.product_id.id not in diccionario_degustacion_devolucion[lineas_devo.product_id.categ_id.id]['productos_hijos']:
                                    diccionario_degustacion_devolucion[lineas_devo.product_id.categ_id.id]['productos_hijos'][lineas_devo.product_id.id]={
                                    'nombre_producto':lineas_devo.product_id.name,
                                    'cantidad':0,
                                    'cantidad_devolucion':0,
                                    'precio_coste':lineas_devo.product_id.standard_price,
                                    'total_cantidad_precio':0,
                                    'total_cantidad_precio_devo':0,
                                    'total_producto_venta':0,
                                    }
                        if lineas_devo.product_id.categ_id.id in diccionario_degustacion_devolucion and lineas_devo.product_id.id in diccionario_degustacion_devolucion[lineas_devo.product_id.categ_id.id]['productos_hijos']:
                            cantidad += lineas_devo.qty_done
                            diccionario_degustacion_devolucion[lineas_devo.product_id.categ_id.id]['productos_hijos'][lineas_devo.product_id.id]['cantidad_devolucion']+=cantidad
                            diccionario_degustacion_devolucion[lineas_devo.product_id.categ_id.id]['productos_hijos'][lineas_devo.product_id.id]['total_cantidad_precio_devo'] = round((diccionario_degustacion_devolucion[lineas_devo.product_id.categ_id.id]['productos_hijos'][lineas_devo.product_id.id]['cantidad_devolucion']*diccionario_degustacion_devolucion[lineas_devo.product_id.categ_id.id]['productos_hijos'][lineas_devo.product_id.id]['precio_coste']),2)

            devoluciones2 = self.env['stock.picking'].search([('picking_type_id','=',devolucion),('scheduled_date','>=',str(fecha_inicio_hora)),('scheduled_date','<=',str(fecha_final_hora))])

            total_importe_devo=0
            total_columna_devo=0
            for devuelto in devoluciones2:
                for lineas1 in devuelto.move_line_ids_without_package:
                    for categoria1 in w.categoria_ids:
                        if lineas1.product_id.categ_id.id == categoria1.id and lineas1.product_id.categ_id.parent_id.id != False:
                            if lineas1.product_id.categ_id.id in diccionario_degustacion_devolucion and lineas1.product_id.id in diccionario_degustacion_devolucion[lineas1.product_id.categ_id.id]['productos_hijos']:
                                total_importe_devo = round((lineas1.qty_done * lineas1.product_id.standard_price),2)
                                total_columna_devo += round(total_importe_devo,2)


            # Verificacion de pedidos en el rango de fechas
            for tienda in w.tienda_ids:
                pedidos = self.env['pos.order'].search([('session_id.config_id','=',tienda.id),('date_order','>=',str(fecha_inicio_hora)),('date_order','<=',str(fecha_final_hora))])
                for pedido in pedidos:
                    for lineas_pedido in pedido.lines:
                        venta_producto=0
                        if lineas_pedido.product_id.categ_id.id in diccionario_degustacion_devolucion and lineas_pedido.product_id.id in diccionario_degustacion_devolucion[lineas_pedido.product_id.categ_id.id]['productos_hijos']:
                            venta_producto += lineas_pedido.price_subtotal_incl
                            diccionario_degustacion_devolucion[lineas_pedido.product_id.categ_id.id]['productos_hijos'][lineas_pedido.product_id.id]['total_producto_venta'] = round(venta_producto,2)


            for primera_llave in diccionario_degustacion_devolucion:
                suma_degustacion =0
                suma_devolucion=0
                suma_ventas=0
                for segunda_llave in diccionario_degustacion_devolucion[primera_llave]['productos_hijos']:
                    suma_degustacion += diccionario_degustacion_devolucion[primera_llave]['productos_hijos'][segunda_llave]['total_cantidad_precio']
                    suma_devolucion += diccionario_degustacion_devolucion[primera_llave]['productos_hijos'][segunda_llave]['total_cantidad_precio_devo']
                    suma_ventas += diccionario_degustacion_devolucion[primera_llave]['productos_hijos'][segunda_llave]['total_producto_venta']
                diccionario_degustacion_devolucion[primera_llave]['degustacion'] = suma_degustacion
                diccionario_degustacion_devolucion[primera_llave]['devolucion'] = suma_devolucion
                diccionario_degustacion_devolucion[primera_llave]['importe_pedido'] = suma_ventas
            tot_devo = 0

            for pk in diccionario_degustacion_devolucion:
                tot_devo += diccionario_degustacion_devolucion[pk]['devolucion']

            porcentaje_devol=0
            calculo = 0
            calculo_ideal=0
            for pkey in diccionario_degustacion_devolucion:
                porcentaje_devol = round(( diccionario_degustacion_devolucion[pkey]['devolucion'] / tot_devo )*100,2)
                calculo = round((diccionario_degustacion_devolucion[pkey]['devolucion']/total_columna_devo),2)
                calculo_ideal = round((diccionario_degustacion_devolucion[pkey]['importe_pedido'] * 0.02),2)
                diccionario_degustacion_devolucion[pkey]['porcentaje_devo'] = calculo
                diccionario_degustacion_devolucion[pkey]['porcentaje_part_familia'] = porcentaje_devol;
                diccionario_degustacion_devolucion[pkey]['imp_dev_ideal'] = round(calculo_ideal,2)
                diferencia_devolucion_ideal = round((diccionario_degustacion_devolucion[pkey]['devolucion']-diccionario_degustacion_devolucion[pkey]['imp_dev_ideal']),2)
                diccionario_degustacion_devolucion[pkey]['dif_dev_ideal']=round(diferencia_devolucion_ideal,2)


            borde = libro.add_format({'border': 2, 'border_color':'#2caad1', 'fg_color': '#067ca1', 'color':'#ffffff','align': 'center'})
            negrita = libro.add_format({'bold': 1, 'fg_color': '#d5d9de'})
            derecha = libro.add_format({'align': 'right'})
            fon_cat_hijas = libro.add_format({'fg_color': '#b8d7ff'})
            dia_inicio = w.fecha_inicio.strftime('%d')
            dia_final = w.fecha_final.strftime('%d')
            mes_final = w.fecha_final.strftime('%m')
            año_final = w.fecha_final.strftime('%Y')

            hoja.write(2,1, 'Devolución y degustación por familia acumulado ' +str(dia_inicio)+' al '+str(dia_final)+' del '+str(mes_final) +' /'+str(año_final), negrita)
            hoja.write(3,1, 'FAMILIA ', borde)
            hoja.write(3,2, 'DEGUS ', borde)
            hoja.write(3,3, 'DEVO ', borde)
            hoja.write(3,4, '%DEVO ', borde)
            hoja.write(3,5, '% PART X FAMILIA ', borde)
            hoja.write(3,6, '% IDEAL DEV ', borde)
            hoja.write(3,7, 'IMP DEV IDEAL ', borde)
            hoja.write(3,8, 'DIF DEV IDEAL A. ', borde)
            fila1 = 4
            total_columna_degusta = 0
            total_columna_devolucion = 0
            total_columna_imp_dev_ideal=0
            total_columna_dif_dev_ideal=0

            for id_cate in diccionario_degustacion_devolucion:
                hoja.write(fila1, 1, str(diccionario_degustacion_devolucion[id_cate]['nombre_categoria_hija_degustacion']), fon_cat_hijas)
                hoja.write(fila1, 2, str(diccionario_degustacion_devolucion[id_cate]['degustacion']), derecha)
                total_columna_degusta += round(diccionario_degustacion_devolucion[id_cate]['degustacion'],2)
                hoja.write(fila1, 3, str(diccionario_degustacion_devolucion[id_cate]['devolucion']), derecha)
                total_columna_devolucion += round(diccionario_degustacion_devolucion[id_cate]['devolucion'],2)
                hoja.write(fila1, 4, str(diccionario_degustacion_devolucion[id_cate]['porcentaje_devo'])+'%', derecha)
                hoja.write(fila1, 5, str(diccionario_degustacion_devolucion[id_cate]['porcentaje_part_familia'])+'%', derecha)
                hoja.write(fila1, 6, str(diccionario_degustacion_devolucion[id_cate]['ideal_dev'])+'%', derecha)
                hoja.write(fila1, 7, str(diccionario_degustacion_devolucion[id_cate]['imp_dev_ideal']), derecha)
                total_columna_imp_dev_ideal += round(diccionario_degustacion_devolucion[id_cate]['imp_dev_ideal'],2)
                hoja.write(fila1, 8, str(diccionario_degustacion_devolucion[id_cate]['dif_dev_ideal']), derecha)
                total_columna_dif_dev_ideal += round(diccionario_degustacion_devolucion[id_cate]['dif_dev_ideal'],2)
                fila1+=1
            negrita = libro.add_format({'bold': 1, 'fg_color': '#5a98bf', 'color':'#ffffff', 'align':'left'})
            hoja.write(fila1,1, 'Total ', negrita)
            negrita = libro.add_format({'bold': 1, 'fg_color': '#5a98bf', 'color':'#ffffff', 'align':'right'})
            hoja.write(fila1,2, str(total_columna_degusta), negrita)
            hoja.write(fila1,3, str(total_columna_devolucion), negrita)
            hoja.write(fila1,4, ' ', negrita)
            hoja.write(fila1,5, ' ', negrita)
            hoja.write(fila1,6, '2%', negrita)
            hoja.write(fila1,7, str(total_columna_imp_dev_ideal), negrita)
            hoja.write(fila1,8, str(total_columna_dif_dev_ideal), negrita)


            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'Repor_degustaciones_devoluciones.xls'})

        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'quemen_reportes.devolucion_familia.wizard',
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
        return self.env.ref('quemen_reportes.quemen_devoluciones_familia.wizard').report_action([], data=datas)
