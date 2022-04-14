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
from datetime import date, timezone
import dateutil.parser
import pytz

class VentasWizard(models.TransientModel):
    _name = 'quemen_reportes.reporte_ventas.wizard'
    _description = "Reporte de ventas"

    fecha_inicio = fields.Datetime('Fecha inicio', required=True)
    fecha_final = fields.Datetime('Fecha final', required=True)
    tienda_ids = fields.Many2many('pos.config','quemen_ventas_tienda',string="Tiendas", required=True)
    estado = fields.Selection([('A','pagado'),
    ('B','publicado'),
    ('C', 'facturado'),
    ('D', 'pagado_publicado'),
    ('E', 'pagado_facturado'),
    ('F', 'publicado_facturado')], string="Estado")

    archivo = fields.Binary('Archivo')
    name = fields.Char('File Name', size=32)

    def generando_excel (self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')
            logging.warn("Si funciono el otro")
            #Tamaño de la fila
            hoja.set_row(2, 15)
            hoja.set_row(1,25)

            formato_titulo = libro.add_format({'size': 18, 'color':'#ffffff', 'align':'center', 'fg_color':'#a0a2a3'})
            formato_subtitulo = libro.add_format({'size': 10, 'color':'#000000', 'align':'left', 'fg_color':'#c5c8c9', 'border_color':'#ffffff', 'border': 2,})
            hoja.merge_range('A2:N2', 'Reporte de tickets de venta', formato_titulo)

            #Tamaño de la columna
            hoja.set_column('A:A',10)
            hoja.set_column('B:B',20)
            hoja.set_column('C:C',15)
            hoja.set_column('E:F',15)
            hoja.set_column('G:H',20)
            hoja.set_column('I:I',30)
            hoja.set_column('K:L',15)
            hoja.set_column('M:N',15)

            hoja.write(2,0, 'Tienda(s): ', formato_subtitulo)
            hoja.write(3,0, 'Estado(s): ', formato_subtitulo)
            hoja.write(4,0, 'Fecha(s): ', formato_subtitulo)
            hoja.write(5,0, 'Hora: ', formato_subtitulo)

            formato_subtitulo = libro.add_format({'size': 10, 'color':'#000000', 'align':'center', 'fg_color':'#c882cf', 'border_color':'#ffffff', 'border': 2,})
            hoja.write(7,0, 'Tienda ', formato_subtitulo)
            hoja.write(7,1, 'Folio ', formato_subtitulo)
            hoja.write(7,2, 'Fecha ', formato_subtitulo)
            hoja.write(7,3, 'Hora ', formato_subtitulo)
            hoja.write(7,4, 'Usuario ', formato_subtitulo)
            hoja.write(7,5, 'Estatus ', formato_subtitulo)
            hoja.write(7,6, 'Tipo de pago ', formato_subtitulo)
            hoja.write(7,7, 'Código de barras ', formato_subtitulo)
            hoja.write(7,8, 'Descripción ', formato_subtitulo)
            hoja.write(7,9, 'Cantidad ', formato_subtitulo)
            hoja.write(7,10, 'Precio unitario ', formato_subtitulo)
            hoja.write(7,11, 'Descuento detalle ', formato_subtitulo)
            hoja.write(7,12, 'Subtotal detalle ', formato_subtitulo)
            hoja.write(7,13, 'Total detalle ', formato_subtitulo)


            formato_texto = libro.add_format({'size': 10, 'color':'#000000', 'align':'center', 'border_color':'#000000', 'border': 1,})
            formato_texto_cantidades = libro.add_format({'size': 10, 'color':'#000000', 'align':'right', 'border_color':'#000000', 'border': 1,})
            formato_fecha_inicio = w.fecha_inicio.strftime('%d/%m/%Y')
            formato_fecha_final = w.fecha_final.strftime('%d/%m/%Y')
            timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
            hora_inicio= w.fecha_inicio.astimezone(timezone).strftime('%H:%M:%S')
            hora_final = w.fecha_final.astimezone(timezone).strftime('%H:%M:%S')
            logging.warn(hora_inicio)
            logging.warn(w.estado)
            tipo_estado=''
            if w.estado=='A':
                tipo_estado='pagado'
            if w.estado=='B':
                tipo_estado='publicado'
            if w.estado=='C':
                tipo_estado='facturado'
            if w.estado == 'D':
                tipo_estado='pagado_publicado'
            if w.estado == 'E':
                tipo_estado='pagado_facturado'
            if w.estado == 'F':
                tipo_estado='publicado_facturado'

            hoja.write(3,1, str(tipo_estado), formato_texto)
            hoja.write(4,1, str(formato_fecha_inicio)+' - '+str(formato_fecha_final), formato_texto)
            hoja.write(5,1, str(hora_inicio)+' - '+str(hora_final), formato_texto)
            fila=8
            for tienda in w.tienda_ids:
                logging.warn("La tienda es : "+ str(tienda))
                hoja.write(2,1, str(tienda.name), formato_texto)
                pedidos = self.env['pos.order'].search([('session_id.config_id', '=', tienda.id), ('date_order', '>=', w.fecha_inicio), ('date_order', '<=', w.fecha_final)])
                for pedido in pedidos:
                    varios_pagos=[]
                    for lineas in pedido.lines:
                        logging.warn("Que estado tiene?")
                        logging.warn(pedido.name +' '+ pedido.state)
                        if tipo_estado == 'facturado' and pedido.state == 'invoiced' or tipo_estado == 'publicado_facturado' and pedido.state == 'invoiced' or tipo_estado == 'pagado_facturado' and pedido.state == 'invoiced':
                            tipo_estado1='Facturado'
                            hoja.write(fila,0, str(pedido.session_id.config_id.name), formato_texto)
                            hoja.write(fila,1, str(pedido.name), formato_texto)
                            formato_fecha1= pedido.date_order.astimezone(timezone).strftime('%d/%m/%Y')
                            formato_hora1= pedido.date_order.astimezone(timezone).strftime('%H:%M:%S')
                            hoja.write(fila,2, str(formato_fecha1), formato_texto)
                            hoja.write(fila,3, str(formato_hora1), formato_texto)
                            hoja.write(fila,4, str(pedido.user_id.name), formato_texto)
                            hoja.write(fila,5, str(tipo_estado1), formato_texto)
                            if len(pedido.payment_ids) == 1:
                                for lineas_pago in pedido.payment_ids:
                                    hoja.write(fila,6, str(lineas_pago.payment_method_id.name), formato_texto)
                            if len(pedido.payment_ids) > 1:
                                for lineas_pago in pedido.payment_ids:
                                    varios_pagos.append(lineas_pago.payment_method_id.name)
                                varios_pagos_join = '-'.join(varios_pagos)
                                hoja.write(fila,6, str(varios_pagos_join), formato_texto)

                            hoja.write(fila,7, str(lineas.product_id.barcode), formato_texto)
                            hoja.write(fila,8, str(lineas.product_id.name), formato_texto)
                            hoja.write(fila,9, str(lineas.qty), formato_texto_cantidades)
                            hoja.write(fila,10, str(round(lineas.price_unit,2)), formato_texto_cantidades)
                            hoja.write(fila,11, str(round(lineas.discount,2)), formato_texto_cantidades)
                            hoja.write(fila,12, str(round(lineas.price_subtotal,2)), formato_texto_cantidades)
                            hoja.write(fila,13, str(round(lineas.price_subtotal_incl,2)), formato_texto_cantidades)
                            logging.warn("Primera Verificación bien Woajaajajaj")
                            fila+=1

                        if tipo_estado == 'publicado' and pedido.state == 'done' or tipo_estado =='pagado_publicado' and pedido.state == 'done' or tipo_estado =='publicado_facturado' and pedido.state == 'done':
                            tipo_estado1 = 'Publicado'
                            hoja.write(fila,0, str(pedido.session_id.config_id.name), formato_texto)
                            hoja.write(fila,1, str(pedido.name), formato_texto)
                            formato_fecha1= pedido.date_order.astimezone(timezone).strftime('%d/%m/%Y')
                            formato_hora1= pedido.date_order.astimezone(timezone).strftime('%H:%M:%S')
                            hoja.write(fila,2, str(formato_fecha1), formato_texto)
                            hoja.write(fila,3, str(formato_hora1), formato_texto)
                            hoja.write(fila,4, str(pedido.user_id.name), formato_texto)
                            hoja.write(fila,5, str(tipo_estado1), formato_texto)
                            if len(pedido.payment_ids) == 1:
                                for lineas_pago in pedido.payment_ids:
                                    hoja.write(fila,6, str(lineas_pago.payment_method_id.name), formato_texto)
                            if len(pedido.payment_ids) > 1:
                                for lineas_pago in pedido.payment_ids:
                                    varios_pagos.append(lineas_pago.payment_method_id.name)
                                varios_pagos_join = '-'.join(varios_pagos)
                                hoja.write(fila,6, str(varios_pagos_join), formato_texto)

                            hoja.write(fila,7, str(lineas.product_id.barcode), formato_texto)
                            hoja.write(fila,8, str(lineas.product_id.name), formato_texto)
                            hoja.write(fila,9, str(lineas.qty), formato_texto_cantidades)
                            hoja.write(fila,10, str(round(lineas.price_unit,2)), formato_texto_cantidades)
                            hoja.write(fila,11, str(round(lineas.discount,2)), formato_texto_cantidades)
                            hoja.write(fila,12, str(round(lineas.price_subtotal,2)), formato_texto_cantidades)
                            hoja.write(fila,13, str(round(lineas.price_subtotal_incl,2)), formato_texto_cantidades)
                            logging.warn("Segunda Verificación bien hecha")
                            fila+=1

                        if tipo_estado == 'pagado' and pedido.state == 'paid' or tipo_estado=='pagado_facturado' and pedido.state == 'paid' or tipo_estado=='pagado_publicado' and pedido.state == 'paid':
                            tipo_estado1 = 'Pagado'
                            hoja.write(fila,0, str(pedido.session_id.config_id.name), formato_texto)
                            hoja.write(fila,1, str(pedido.name), formato_texto)
                            formato_fecha1= pedido.date_order.astimezone(timezone).strftime('%d/%m/%Y')
                            formato_hora1= pedido.date_order.astimezone(timezone).strftime('%H:%M:%S')
                            hoja.write(fila,2, str(formato_fecha1), formato_texto)
                            hoja.write(fila,3, str(formato_hora1), formato_texto)
                            hoja.write(fila,4, str(pedido.user_id.name), formato_texto)
                            hoja.write(fila,5, str(tipo_estado1), formato_texto)
                            if len(pedido.payment_ids) == 1:
                                for lineas_pago in pedido.payment_ids:
                                    hoja.write(fila,6, str(lineas_pago.payment_method_id.name), formato_texto)
                            if len(pedido.payment_ids) > 1:
                                for lineas_pago in pedido.payment_ids:
                                    varios_pagos.append(lineas_pago.payment_method_id.name)
                                varios_pagos_join = '-'.join(varios_pagos)
                                hoja.write(fila,6, str(varios_pagos_join), formato_texto)

                            hoja.write(fila,7, str(lineas.product_id.barcode), formato_texto)
                            hoja.write(fila,8, str(lineas.product_id.name), formato_texto)
                            hoja.write(fila,9, str(lineas.qty), formato_texto_cantidades)
                            hoja.write(fila,10, str(round(lineas.price_unit,2)), formato_texto_cantidades)
                            hoja.write(fila,11, str(round(lineas.discount,2)), formato_texto_cantidades)
                            hoja.write(fila,12, str(round(lineas.price_subtotal,2)), formato_texto_cantidades)
                            hoja.write(fila,13, str(round(lineas.price_subtotal_incl,2)), formato_texto_cantidades)
                            logging.warn("Tercera Verificación bien Woajajaj")
                            fila+=1


            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'Reporte_ventas.xls'})

        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'quemen_reportes.reporte_ventas.wizard',
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
        return self.env.ref('quemen_reportes.quemen_reporte_ventas.wizard').report_action([], data=datas)
