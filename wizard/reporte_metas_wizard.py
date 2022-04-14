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
from datetime import date, timezone, timedelta, datetime
import calendar
import dateutil.parser
import pytz

class MetasWizard(models.TransientModel):
    _name = 'quemen_reportes.reporte_metas.wizard'
    _description = "Reporte de metas"

    fecha_inicio = fields.Date('Fecha inicio', required=True)
    fecha_final = fields.Date('Fecha final', required=True)
    tienda_ids = fields.Many2many('pos.config','quemen_metas_tienda',string="Tiendas", required=True)

    archivo = fields.Binary('Archivo')
    name = fields.Char('File Name', size=32)

    def generando_excel (self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')
            logging.warn("Que onda si funcione?")

            formato_titulo = libro.add_format({'size': 13, 'color':'#000000', 'align':'center', 'fg_color':'#a0a2a3'})
            formato_titulo_totales = libro.add_format({'size': 13, 'color':'#FFFFFF', 'align':'center', 'fg_color':'#570091', 'border_color':'#000000', 'border':1})
            formato_fechas = libro.add_format({'size': 10, 'color':'#000000', 'align':'center', 'border_color':'#000000', 'border':1})

            month_year = w.fecha_inicio.strftime('%m %Y')
            menos_uno = int(w.fecha_inicio.strftime('%Y'))-1
            day_month_start = w.fecha_inicio.strftime('%d/%m')
            final_day_month = w.fecha_final.strftime('%d/%m')

            fecha_inicio_pasado = day_month_start+'/'+str(menos_uno)
            fecha_final_pasado = final_day_month+'/'+str(menos_uno)

            #mes año pasado
            month_last_year = w.fecha_inicio.strftime('%m')+' '+str(menos_uno)

            #Año actual
            last_year = int(w.fecha_inicio.strftime('%Y'))-1

            #Tamaño de la fila
            # hoja.set_row(1,20)

            #Tamaño de las columnas
            hoja.set_column('A:B',10)
            hoja.set_column('C:C',17)
            hoja.set_column('G:G',25)
            hoja.set_column('I:I',25)
            hoja.set_column('K:K',25)

            hoja.merge_range('A1:C1', 'Reporte de metas', formato_fechas)
            hoja.write(1,0, 'Fecha inicio: ', formato_fechas)
            hoja.write(1,1, str(w.fecha_inicio.strftime("%d/%m/%Y")), formato_fechas)
            hoja.write(2,0, 'Fecha final: ', formato_fechas)
            hoja.write(2,1, str(w.fecha_final.strftime("%d/%m/%Y")), formato_fechas)
            hoja.write(3,0, 'Tienda(s): ', formato_fechas)

            hoja.merge_range('A6:B6', 'Día del mes '+str(month_last_year) )
            hoja.write(5,2, 'Totales '+str(month_last_year), formato_titulo_totales)
            hoja.write(6,2, 'vta '+str(last_year), formato_fechas)

            hoja.merge_range('E6:F6', 'Del mes '+str(month_year) )
            hoja.write(5,6, 'Totales metas del '+str(month_year), formato_titulo_totales)
            formato_ventas_reales = libro.add_format({'size': 13, 'color':'#FFFFFF', 'align':'center', 'fg_color':'#c67cf7', 'border_color':'#000000', 'border':1})
            hoja.write(5,8, 'Ventas reales de '+str(month_year), formato_ventas_reales)

            formato_cumplimiento_titulo = libro.add_format({'size': 13, 'color':'#000000', 'align':'center', 'fg_color':'#eed4ff', 'border_color':'#000000', 'border':1})
            hoja.write(5,10, '% Cumplimiento de meta '+str(month_year), formato_cumplimiento_titulo)



            #Codigo para obtener un rango de fechas
            lista_fechas = [(w.fecha_inicio + timedelta(days=d)).strftime("%d/%m/%Y") for d in range((w.fecha_final-w.fecha_inicio).days +1)]
            tipo_date_inicio = datetime.strptime(fecha_inicio_pasado, '%d/%m/%Y')
            tipo_date_final = datetime.strptime(fecha_final_pasado, '%d/%m/%Y')
            lista_fechas_pasado = [(tipo_date_inicio + timedelta(days=d)).strftime("%d/%m/%Y") for d in range((tipo_date_final-tipo_date_inicio).days +1)]

            fila = 7

            lista_tiendas=[]
            diccionario_metas = {}
            diccionario_pedidos = {}
            for tienda in w.tienda_ids:
                logging.warning("Nombre de la tienda: "+ tienda.name)
                metas = self.env['quemen.metas'].search([('tienda_almacen_id.id', '=', tienda.id), ('fecha_inicio', '>=', w.fecha_inicio), ('fecha_final', '<=', w.fecha_final)])
                for meta in metas:
                    if meta.fecha_inicio not in diccionario_metas:
                        diccionario_metas[meta.fecha_inicio.strftime("%d/%m/%Y")]={
                        'fecha':meta.fecha_inicio.strftime("%d/%m/%Y"),
                        'total':0
                        }
                    if meta.fecha_inicio.strftime("%d/%m/%Y") in diccionario_metas:
                        for lineas in meta.linea_ids:
                            diccionario_metas[meta.fecha_inicio.strftime("%d/%m/%Y")]['total']+=lineas.metaTotal
                lista_tiendas.append(tienda.name)

                pedidos = self.env['pos.order'].search([('session_id.config_id', '=', tienda.id), ('date_order', '>=', w.fecha_inicio), ('date_order', '<=', w.fecha_final)])
                for pedido in pedidos:
                    if pedido.date_order.strftime("%d/%m/%Y") not in diccionario_pedidos:
                        diccionario_pedidos[pedido.date_order.strftime("%d/%m/%Y")]={
                        'fecha': pedido.date_order.strftime("%d/%m/%Y"),
                        'total':0
                        }
                    if pedido.date_order.strftime("%d/%m/%Y") in diccionario_pedidos:
                        diccionario_pedidos[pedido.date_order.strftime("%d/%m/%Y")]['total']+=round(pedido.amount_paid,2)

            for fecha in lista_fechas:
                hoja.write(fila,4, str(fecha), formato_fechas)
                string_date = datetime.strptime(fecha, '%d/%m/%Y')
                nombre_día =calendar.day_name[string_date.weekday()]

                if nombre_día == 'sábado' or nombre_día == 'domingo':
                    formato_fechas_fines = libro.add_format({'size': 10, 'color':'#FFFFFF', 'align':'center', 'border_color':'#000000', 'border':1, 'fg_color':'#9a72b5'})
                    hoja.write(fila,5, str(calendar.day_name[string_date.weekday()]), formato_fechas_fines)
                else:
                    hoja.write(fila,5, str(calendar.day_name[string_date.weekday()]), formato_fechas)

                if fecha in diccionario_metas:
                    hoja.write(fila,6, str(diccionario_metas[fecha]['total']), formato_fechas)

                if fecha in diccionario_pedidos:
                    hoja.write(fila,8, str(diccionario_pedidos[fecha]['total']), formato_fechas)

                if fecha in diccionario_metas and fecha in diccionario_pedidos:
                    if diccionario_metas[fecha]['fecha'] == diccionario_pedidos[fecha]['fecha']:
                        if(diccionario_metas[fecha]['total'] and diccionario_pedidos[fecha]['total']) > 0:
                            cumplimiento_meta = round(((diccionario_pedidos[fecha]['total']/diccionario_metas[fecha]['total'])*100) ,2)
                            hoja.write(fila,10, str(cumplimiento_meta)+'%', formato_fechas)


                fila+=1

            fila=7
            nombre_día =''
            diccionario_metas_atras = {}
            for tienda in w.tienda_ids:
                metas1 = self.env['quemen.metas'].search([('tienda_almacen_id.id', '=', tienda.id), ('fecha_inicio', '>=', str(fecha_inicio_pasado)), ('fecha_final', '<=', str(fecha_final_pasado))])
                logging.warn("metas1")
                logging.warn(metas1)
                for meta1 in metas1:
                    if meta1.fecha_inicio not in diccionario_metas_atras:
                        diccionario_metas_atras[meta1.fecha_inicio.strftime("%d/%m/%Y")]={
                        'total':0
                        }
                    if meta1.fecha_inicio.strftime("%d/%m/%Y") in diccionario_metas_atras:
                        for lineas in meta1.linea_ids:
                            diccionario_metas_atras[meta1.fecha_inicio.strftime("%d/%m/%Y")]['total']+=lineas.metaTotal


            for fecha1 in lista_fechas_pasado:
                hoja.write(fila,0, str(fecha1), formato_fechas)
                string_date = datetime.strptime(fecha1, '%d/%m/%Y')
                nombre_día =calendar.day_name[string_date.weekday()]

                if nombre_día == 'sábado' or nombre_día == 'domingo':
                    formato_fechas_fines = libro.add_format({'size': 10, 'color':'#FFFFFF', 'align':'center', 'border_color':'#000000', 'border':1, 'fg_color':'#9a72b5'})
                    hoja.write(fila,1, str(calendar.day_name[string_date.weekday()]), formato_fechas_fines)
                else:
                    hoja.write(fila,1, str(calendar.day_name[string_date.weekday()]), formato_fechas)
                if fecha1 in diccionario_metas_atras:
                    hoja.write(fila,2, str(diccionario_metas_atras[fecha1]['total']), formato_fechas)
                fila+=1

            n_tiendas = ', '.join(lista_tiendas)
            hoja.write(3,1, str(n_tiendas), formato_fechas)
            logging.warn("diccionario_metas_atras")
            logging.warn(diccionario_metas_atras)
            logging.warn(" ")
            logging.warn(diccionario_metas)
            logging.warn(lista_tiendas)
            logging.warn("")
            logging.warn("diccionario_pedidos")
            logging.warn(diccionario_pedidos)
            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'Reporte_metas.xls'})

        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'quemen_reportes.reporte_metas.wizard',
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
        return self.env.ref('quemen_reportes.quemen_reporte_metas.wizard').report_action([], data=datas)
