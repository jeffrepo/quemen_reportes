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

class DescuentoWizard(models.TransientModel):
    _name = 'quemen_reportes.reporte_descuento.wizard'
    _description = "Reporte de descuentos"

    fecha_inicio = fields.Date('Fecha inicio', required=True)
    fecha_final = fields.Date('Fecha final', required=True)
    tienda_ids = fields.Many2many('pos.config','quemen_relacion_tienda',string="Tiendas", required=True)

    archivo = fields.Binary('Archivo')
    name = fields.Char('File Name', size=32)

    def generando_excel (self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')


            formato_titulo = libro.add_format({'size': 18, 'color':'#ffffff', 'align':'center', 'fg_color':'#7a0060'})
            #Tamaño de la fila
            hoja.set_row (2, 30)
            hoja.set_row (4, 20)
            hoja.merge_range('B3:L3', 'Reporte descuentos del ' +str(w.fecha_inicio)+' a '+str(w.fecha_final), formato_titulo)

            formato_subtitulo = libro.add_format({'size': 11, 'color':'#ffffff', 'align':'center', 'fg_color':'#7a0060', 'border_color':'#ffffff', 'border': 2,})
            formato_cantidades = libro.add_format({'align':'right', 'border_color':'#000000', 'border': 1,})
            formato_strings = libro.add_format({'align':'left', 'border_color':'#000000', 'border': 1,})
            hoja.write(4,0, 'Nombre', formato_subtitulo)
            hoja.write(4,1, 'Razón social', formato_subtitulo)
            hoja.write(4,2, 'Fecha hora', formato_subtitulo)
            hoja.write(4,3, 'Tienda', formato_subtitulo)
            hoja.write(4,4, 'Folio', formato_subtitulo)
            hoja.write(4,5, 'Producto', formato_subtitulo)
            hoja.write(4,6, 'Precio', formato_subtitulo)
            hoja.write(4,7, 'Cantidad', formato_subtitulo)
            hoja.write(4,8, 'Descuento porcentual', formato_subtitulo)
            hoja.write(4,9, 'Descuento monto', formato_subtitulo)
            hoja.write(4,10, 'Total', formato_subtitulo)
            hoja.write(4,11, 'Tipo', formato_subtitulo)
            hoja.write(4,12, 'Descuento nombre', formato_subtitulo)
            #Tamaño de las columnas
            hoja.set_column('A:B', 30)
            hoja.set_column('C:C', 20)
            hoja.set_column('D:F', 30)
            hoja.set_column('E:E', 25)
            hoja.set_column('G:H', 15)
            hoja.set_column('I:J', 30)
            hoja.set_column('K:K', 15)
            hoja.set_column('L:L', 20)
            hoja.set_column('M:M', 30)

            fila= 5
            ids_tienda = w.tienda_ids
            for id_tienda in ids_tienda:
                fecha_inicio_hora = ' '
                fecha_inicio_hora = str(w.fecha_inicio)+' 00:00:00'
                fecha_final_hora = ' '
                fecha_final_hora = str(w.fecha_final)+' 23:59:59'
                pedidos = self.env['pos.order'].search([('session_id.config_id','=',id_tienda.id),('date_order','>=',str(fecha_inicio_hora)),('date_order','<=',str(fecha_final_hora))])

                fecha_pedido=''
                for pedido in pedidos:
                    descuento_porcentual=0
                    # descuento=0
                    fecha_pedido = pedido.date_order
                    precio_unitario = 0
                    for lineas_pedido in pedido.lines:
                        descuento=0
                        descuento = round(lineas_pedido.discount,2)
                        if descuento > 0:
                            precio_unitario = round(lineas_pedido.price_unit,2)
                            hoja.write(fila,0, str(pedido.partner_id.name), formato_strings)
                            hoja.write(fila,1, str(pedido.partner_id.name), formato_strings)
                            hoja.write(fila,2, str(fecha_pedido), formato_strings)
                            hoja.write(fila,3, str(pedido.session_id.config_id.name), formato_strings)
                            hoja.write(fila,4, str(pedido.name), formato_strings)
                            hoja.write(fila,5, str(lineas_pedido.product_id.name), formato_strings)
                            hoja.write(fila,6, str(precio_unitario), formato_cantidades)
                            cantidad_producto = round(lineas_pedido.qty,2)
                            hoja.write(fila,7, str(cantidad_producto), formato_cantidades)
                            descuento_porcentual = round(lineas_pedido.discount,2)
                            hoja.write(fila,8, str(descuento_porcentual), formato_cantidades)
                            conversion_porcentaje = round((descuento_porcentual/100),9)
                            descuento_monto= round((lineas_pedido.price_subtotal_incl*conversion_porcentaje),2)
                            hoja.write(fila,9, str(descuento_monto), formato_cantidades)
                            calculo_total= round((lineas_pedido.price_subtotal_incl-descuento_monto),2)
                            hoja.write(fila,10, str(calculo_total), formato_cantidades)
                            if lineas_pedido.promocion_id:
                                if lineas_pedido.promocion_id.tipo_select == "desc":
                                    hoja.write(fila,11, "Descuento", formato_cantidades)
                                if lineas_pedido.promocion_id.tipo_select == "promo":
                                    hoja.write(fila,11, "Promoción", formato_cantidades)
                                hoja.write(fila,12, lineas_pedido.promocion_id.name, formato_cantidades)

                            fila+=1

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'Reporte_descuento.xls'})

        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'quemen_reportes.reporte_descuento.wizard',
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
        return self.env.ref('quemen_reportes.quemen_reporte_descuento.wizard').report_action([], data=datas)
