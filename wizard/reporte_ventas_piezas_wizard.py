# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict
import logging
import xlsxwriter
import io
import base64
import dateutil.parser
import datetime
import time
from datetime import date, timezone, timedelta
import pytz

class VentasPiezasWizard(models.TransientModel):
    _name ='quemen_reportes.reporte_ventas_piezas.wizard'
    _description =" Reporte de ventas de piezas"

    fecha_inicio = fields.Date('Fecha inicio', required=True)
    fecha_final = fields.Date('Fecha final', required=True)
    tienda_ids = fields.Many2many('pos.config', 'quemen_relacion_pzas', string='Tiendas', required=True)
    categorias_ids = fields.Many2many('product.category', 'quemen_categoria_rel', string='Categorias')

    archivo = fields.Binary('Archivo')
    name = fields.Char('File Name', size=32)

    def generando_excel(self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')

            #Tamaño de la fila
            hoja.set_row(1,15)
            # hoja.set_row(2, 12)

            #Tamaño de las columnas
            hoja.set_column('B:B',28)
            hoja.set_column('C:C', 20)
            hoja.set_column('D:D', 12)

            formato_titulo = libro.add_format({'size': 11, 'color':'#000000', 'align':'left', 'fg_color':'#a0a2a3'})
            formato_subtitulo = libro.add_format({'size': 10,  'align':'left', 'border_color':'#000000', 'border': 1,})
            formato_cantidades = libro.add_format({'size': 10,  'align':'right', 'border_color':'#000000', 'border': 1,})
            hoja.merge_range('B2:G2', 'DETALLE DE REPORTE GLOBAL POR DÍA ', formato_titulo)

            hoja.write(3,1, 'Concentrado de ventas por día' )
            hoja.write(4,1, 'Fecha generación ', formato_subtitulo)
            formato_fecha_inicio = w.fecha_inicio.strftime('%d/%m/%Y')
            formato_fecha_final = w.fecha_final.strftime('%d/%m/%Y')
            timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
            hoja.write(4,2, str(formato_fecha_inicio)+' - '+str(formato_fecha_final), formato_subtitulo)

            hoja.write(5,1, 'Familia ', formato_subtitulo)
            n_categorias = []
            for categoria in w.categorias_ids:
                n_categorias.append(categoria.name)
            n_categorias_join = ', '.join(n_categorias)
            hoja.write(5,2, str(n_categorias_join), formato_subtitulo)

            hoja.write(6,1, 'Grupo', formato_subtitulo)
            hoja.write(7,1, 'Elaboró', formato_subtitulo)
            hoja.write(7,2, str(self.env.user.name), formato_subtitulo)


            hoja.write(9,1, 'Descripción corta', formato_subtitulo)
            hoja.write(9,2, 'Clave', formato_subtitulo)
            hoja.write(9,3, 'Precio actual', formato_subtitulo)

            #Codigo para obtener un rango de fechas
            lista_fechas = [(w.fecha_inicio + timedelta(days=d)).strftime("%d/%m/%Y") for d in range((w.fecha_final-w.fecha_inicio).days +1)]

            columna = 4
            for fecha in lista_fechas:
                hoja.write(9,columna, str(fecha), formato_subtitulo)
                columna+=1

            fila = 10
            diccionario_productos = {}
            diccionario_productos_tienda={}
            tienda_producto_ids=''
            diccionario_fechas_productos={}
            for tienda in w.tienda_ids:
                pedidos = self.env['pos.order'].search([('session_id.config_id', '=', tienda.id), ('date_order', '>=', w.fecha_inicio), ('date_order', '<=', w.fecha_final)])

                for pedido in pedidos:
                    for lineas in pedido.lines:
                        if lineas.product_id.categ_id.parent_id:
                            for categoria1 in w.categorias_ids:
                                if lineas.product_id.categ_id.parent_id.id == categoria1.id:
                                    if lineas.product_id.id not in diccionario_productos:
                                        diccionario_productos[lineas.product_id.id]={
                                        'id': lineas.product_id.id,
                                        'nombre_producto': lineas.product_id.name,
                                        'clave_producto': lineas.product_id.barcode,
                                        'precio_actual':lineas.product_id.lst_price,
                                        'fechas_pedido': [],
                                        }
                                    if tienda.id > 9:
                                        tienda_producto_ids = str(tienda.id)+'-'+str(lineas.product_id.id)
                                    if tienda.id < 10:
                                        tienda_producto_ids = '0'+str(tienda.id)+'-'+str(lineas.product_id.id)
                                    if tienda_producto_ids not in diccionario_productos_tienda:
                                        diccionario_productos_tienda[tienda_producto_ids]={
                                        'id':lineas.product_id.id,
                                        'id_tienda': tienda.id,
                                        'id_tienda_producto':tienda_producto_ids,
                                        'nombre_producto': lineas.product_id.name,
                                        'clave_producto': lineas.product_id.barcode,
                                        'precio_actual':lineas.product_id.lst_price,
                                        'total':0,
                                        }

                        if lineas.product_id.id in diccionario_productos:
                            if lineas.product_id.id <10:
                                fecha_producto = '0'+str(lineas.product_id.id)+'-'+pedido.date_order.astimezone(timezone).strftime("%d/%m/%Y")
                            if lineas.product_id.id >9:
                                fecha_producto = str(lineas.product_id.id)+'-'+pedido.date_order.astimezone(timezone).strftime("%d/%m/%Y")

                            if fecha_producto not in diccionario_fechas_productos:
                                diccionario_fechas_productos[fecha_producto]={
                                'fecha':pedido.date_order.astimezone(timezone).strftime("%d/%m/%Y"),
                                'total':0
                                }
                            diccionario_fechas_productos[fecha_producto]['total']+=round(lineas.price_subtotal_incl, 2)
                        if tienda.id > 9:
                            tienda_producto_ids = str(tienda.id)+'-'+str(lineas.product_id.id)
                        if tienda.id < 10:
                            tienda_producto_ids = '0'+str(tienda.id)+'-'+str(lineas.product_id.id)
                        if tienda_producto_ids in diccionario_productos_tienda:
                            if tienda_producto_ids == diccionario_productos_tienda[tienda_producto_ids]['id_tienda_producto']:
                                diccionario_productos_tienda[tienda_producto_ids]['total'] += round(lineas.price_subtotal_incl,2)


            n_uno=0
            n_dos=2
            id_extraido =0
            for n_fechas in diccionario_fechas_productos:
                id_extraido = int(n_fechas[n_uno:n_dos])
                if int(id_extraido) in diccionario_productos:
                    diccionario_productos[id_extraido]['fechas_pedido'].append(diccionario_fechas_productos[n_fechas])


            for llave in diccionario_productos:
                hoja.write(fila,1, str(diccionario_productos[llave]['nombre_producto']), formato_subtitulo)
                hoja.write(fila,2, str(diccionario_productos[llave]['clave_producto']), formato_subtitulo)
                hoja.write(fila,3, str(diccionario_productos[llave]['precio_actual']), formato_cantidades)
                for list in diccionario_productos[llave]['fechas_pedido']:
                    for llave1 in list:
                        columna=4
                        for fecha_x in lista_fechas:
                            if list['fecha'] == fecha_x:
                                hoja.write(fila,columna, str(list['total']), formato_cantidades)
                            columna+=1
                fila+=1

            fila1 = fila + 5
            fila_columna = 'B'+str(fila1)
            fila_columna1 = 'G'+str(fila1)
            hoja.merge_range( fila_columna+':'+fila_columna1, 'DETALLE DE REPORTE GLOBAL POR TIENDA ', formato_titulo)
            fila1 +=1
            hoja.write(fila1,1, 'Concentrado de ventas por tienda' )
            fila1 +=1
            hoja.write(fila1,1, 'Fecha generación ', formato_subtitulo)

            hoja.write(fila1,2, str(formato_fecha_inicio)+' - '+str(formato_fecha_final), formato_subtitulo)
            fila1 +=1
            hoja.write(fila1,1, 'Familia ', formato_subtitulo)

            hoja.write(fila1,2, str(n_categorias_join), formato_subtitulo)
            fila1+=1
            hoja.write(fila1,1, 'Grupo', formato_subtitulo)
            fila1+=1
            hoja.write(fila1,1, 'Elaboró', formato_subtitulo)
            hoja.write(fila1,2, str(self.env.user.name), formato_subtitulo)

            fila1 +=2
            hoja.write(fila1,1, 'Descripción corta', formato_subtitulo)
            hoja.write(fila1,2, 'Clave', formato_subtitulo)
            hoja.write(fila1,3, 'Precio actual', formato_subtitulo)

            columna1=4
            for tienda in w.tienda_ids:
                hoja.write(fila1,columna1, str(tienda.name), formato_subtitulo)
                columna1+=1

            fila1+=1
            diccionario_productos_ids ={}
            id_extraido_producto=0
            for key in diccionario_productos_tienda:
                id_extraido_product0 = int(key[key.rfind( '-' ) + 1: ])
                if id_extraido_product0 not in diccionario_productos_ids:
                    hoja.write(fila1,1, str(diccionario_productos_tienda[key]['nombre_producto']), formato_subtitulo)
                    hoja.write(fila1,2, str(diccionario_productos_tienda[key]['clave_producto']), formato_subtitulo)
                    hoja.write(fila1,3, str(diccionario_productos_tienda[key]['precio_actual']), formato_subtitulo)
                columna2 = 4
                for tienda2 in w.tienda_ids:
                    id_extraido = int(key[n_uno:n_dos])

                    #Obtener el id despues de un guíon
                    id_extraido_producto = int(key[key.rfind( '-' ) + 1: ])

                    if tienda2.id == id_extraido:
                        if id_extraido_producto not in diccionario_productos_ids:
                            hoja.write(fila1,columna2, str(diccionario_productos_tienda[key]['total']), formato_subtitulo)
                            diccionario_productos_ids[id_extraido_producto]={
                            'fila':fila1,
                            'id':id_extraido_producto
                            }
                        if id_extraido_producto in diccionario_productos_ids:
                            hoja.write(diccionario_productos_ids[id_extraido_producto]['fila'],columna2, str(diccionario_productos_tienda[key]['total']), formato_subtitulo)

                    columna2+=1
                fila1+=1


            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'reporte_ventas_piezas.xls'})


        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'quemen_reportes.reporte_ventas_piezas.wizard',
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
        return self.env.ref('quemen_reportes.quemen_reporte_ventas_piezas.wizard').report_action([], data=datas)
