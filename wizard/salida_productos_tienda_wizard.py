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

class PruebaWizard(models.TransientModel):
    # modelo es el _name
    _name = 'quemen_reportes.salida_productos_tienda.wizard'
    _description = "Reporte para pasteleria "

    fecha_inicio = fields.Datetime('Fecha inicio')
    fecha_final = fields.Datetime('Fecha final')
    archivo = fields.Binary('Archivo')
    name = fields.Char('File Name', size=32)
    # tipo_salida_ids = fields.Selection([ ('type1', 'Type 1'),('type2', 'Type 2'),],'Type', default = 'type1')
    tipo_salida_ids = fields.Many2many('stock.picking.type','quemen_reportes_tipo_rel',string="Tipo de salida")
    # fields.Many2many('stock.picking.type','quemen_reportes_tipo_rel',string="Tipo de salida")
    categoria_ids = fields.Many2many('product.category','quemen_reportes_categoria_rel',string="Categoria")
    consolidado_tienda = fields.Boolean(string="Consolidado por tienda")
    consolidado_dia = fields.Boolean(string="Consolidado por día")
    tienda_ids = fields.Many2many('stock.warehouse','quemen_reportes_tienda_rel',string="Tiendas")



    def generar_excel(self):

        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')

            merge_format = libro.add_format({'align': 'center'})


            if w.consolidado_tienda==1:
                listado_tiendas=[]
                lista_conceptos=[]
                lista_categoria=[]
                transferencias_filtradas=[]
                productos_filtrados=[]

                s=", "

                transferencias = self.env['stock.picking'].search([('picking_type_id','in', w.tipo_salida_ids.ids),
                ('scheduled_date','>=',str(w.fecha_inicio)),('scheduled_date','<=',str(w.fecha_final)), ('state', '=', 'done')])
                logging.warn(transferencias)
                listado_productos={}

                for transferencia in transferencias:
                    for linea in transferencia.move_ids_without_package:
                        if linea.product_id.id not in listado_productos:
                            lista_tiendas={}
                            for tienda in w.tienda_ids:
                                if tienda.id not in lista_tiendas:
                                    lista_tiendas[tienda.id] = {'nombre_tienda' : tienda.name, 'id' : tienda.id , 'cantidad_productos' : 0}
                            listado_productos[linea.product_id.id] = {'nombre_producto': linea.product_id.name, 'codigo': linea.product_id.default_code, 'tiendas': lista_tiendas}
                            lista_tiendas={}


                logging.warn(listado_productos)
                for transferencia in transferencias:
                    for linea in transferencia.move_ids_without_package:
                        if linea.product_id.id in listado_productos:
                            logging.warn(linea.product_id.id)
                            logging.warn(linea.product_uom_qty)
                            logging.warn(listado_productos[linea.product_id.id]['tiendas'])
                            listado_productos[linea.product_id.id]['tiendas'][transferencia.picking_type_id.warehouse_id.id]['cantidad_productos'] += linea.product_uom_qty
                            logging.warn(listado_productos[linea.product_id.id]['tiendas'])


                logging.warn('Prueba general')
                logging.warn(listado_productos)

                # el siguiente codigo despues de "aux" hasta logging.warn(result) obtiene los objetos repetidos de una lista y en que posicion se encuentran
                # aux = defaultdict(list)
                # for index , item in enumerate(productos_filtrados):
                #     aux[item].append(index)
                # result = {item: indexs for item, indexs in aux.items() if len(indexs) > 1}
                # logging.warn(result)
                productos_filtrados1 = list(set(productos_filtrados))

                hoja.write(2, 2, 'Consolidado por Tienda')
                # hoja.write(2, 3, w.consolidado_tienda[0])
                lista_tiendas_encabezado=[]
                for tienda in w.tienda_ids:
                    lista_tiendas_encabezado.append(tienda.name)
                hoja.write(6, 4, str(s.join(lista_tiendas_encabezado)))

                hoja.write(7, 2, 'Concepto:')

                for concepto in w.tipo_salida_ids:
                    lista_conceptos.append(concepto.name)

                hoja.write(7, 5, str(s.join(lista_conceptos)))

                hoja.write(8, 2, 'Familia: ')

                for categoria in w.categoria_ids:
                    lista_categoria.append(categoria.name)

                hoja.write(8, 5, str(s.join(lista_categoria)))


                hoja.write(9, 2, 'Fecha Inicio:')
                hoja.write(9, 3, w.fecha_inicio, formato_fecha)
                hoja.write(9, 5, w.fecha_final, formato_fecha)
                hoja.write(13, 2, 'Clave')
                hoja.write(13, 3, 'Descripcion')
                fila=14
                fila1=13
                columna=2
                columna1=3
                columna_tiendas=4
                hoja.write(6, 2, 'Tienda: ')
                for store1 in lista_tiendas_encabezado:
                    hoja.write(13, columna_tiendas, str(store1))
                    columna_tiendas += 1


                for clave in listado_productos:
                    hoja.write(fila, columna, str(listado_productos[clave]['codigo']))
                    hoja.write(fila, columna1, str(listado_productos[clave]['nombre_producto']))
                    columna_cantidad = 4
                    for store in listado_productos[clave]['tiendas']:
                        hoja.write(fila, columna_cantidad, str(listado_productos[clave]['tiendas'][store]['cantidad_productos']))
                        columna_cantidad += 1
                    fila = fila + 1




            if w.consolidado_dia==1:
                lista_tiendas=[]
                lista_categoria=[]
                lista_conceptos=[]
                transferencias_filtradas=[]
                productos_filtrados=[]
                listado_de_fechas=[]
                s=", "

                hoja.write(1, 2, 'Consolidado por día')
                hoja.write(3, 5, 'Reporte de salida de productos por día')
                hoja.write(6, 2, 'Tienda: ')

                for tienda in w.tienda_ids:
                    lista_tiendas.append(tienda.name)

                hoja.write(6, 5, str(s.join(lista_tiendas)))
                hoja.write(7, 2, 'Concepto:')

                for concepto in w.tipo_salida_ids:
                    lista_conceptos.append(concepto.name)

                hoja.write(7, 5, str(s.join(lista_conceptos)))

                hoja.write(8, 2, 'Familia')

                for categoria in w.categoria_ids:
                    lista_categoria.append(categoria.name)

                hoja.write(8, 5, str(s.join(lista_categoria)))

                hoja.write(10, 4, str(s.join(listado_de_fechas)))
                hoja.write(9, 2, 'Fecha inicio')
                hoja.write(9, 5, w.fecha_inicio, formato_fecha)
                hoja.write(9, 8, w.fecha_final, formato_fecha)

                transferencias = self.env['stock.picking'].search([('picking_type_id','in', w.tipo_salida_ids.ids),
                ('scheduled_date','>=',str(w.fecha_inicio)),('scheduled_date','<=',str(w.fecha_final)), ('state', '=', 'done')], order='scheduled_date asc')
                listado_productos={}

                for transferencia in transferencias:
                    for linea in transferencia.move_ids_without_package:
                        if linea.product_id.id not in listado_productos:
                            listado_fechas={}
                            for fechas in transferencias:
                                c = fechas.scheduled_date.strftime("%A")
                                b = fechas.scheduled_date
                                d = (b).date()
                                if str(d) not in listado_fechas:
                                    listado_fechas[str(d)]={'id' : tienda.id ,'fechas': str(d),'cantidad_productos' : 0}
                            listado_productos[linea.product_id.id] = {'nombre_producto': linea.product_id.name, 'codigo': linea.product_id.default_code, 'fechas_totales': listado_fechas}
                            listado_fechas={}


            for transferencia in transferencias:
                for linea in transferencia.move_ids_without_package:
                    if linea.product_id.id in listado_productos:
                        for fechas in transferencias:
                            b = fechas.scheduled_date
                            d = (b).date()
                        listado_productos[linea.product_id.id]['fechas_totales'][str(d)]['cantidad_productos']+= linea.product_uom_qty


            lista_fechas_encabezado={}
            for day in transferencias:
                d = day.scheduled_date.strftime("%A")
                c = day.scheduled_date
                e = (c).date()
                logging.warn(d)
                if str(e) not in lista_fechas_encabezado:
                    lista_fechas_encabezado[str(e)]={'fecha': str(e), 'dia': d}
            logging.warn('Listado de productos')
            logging.warn(listado_productos)

            fila = 14
            hoja.write(12, 2, 'Codigo')
            hoja.write(12, 3, 'Descripcion')
            for pro in listado_productos:
                hoja.write(fila, 2, str(listado_productos[pro]['codigo']))
                hoja.write(fila, 3, str(listado_productos[pro]['nombre_producto']))
                columna_cantidad = 4
                for pro2 in listado_productos[pro]['fechas_totales']:
                    hoja.write(fila, columna_cantidad, str(listado_productos[pro]['fechas_totales'][pro2]['cantidad_productos']))
                    columna_cantidad += 1
                fila+=1


            columna = 4
            for ti in lista_fechas_encabezado:
                hoja.write(12, columna, str(lista_fechas_encabezado[ti]['fecha']))
                hoja.write(13, columna, str(lista_fechas_encabezado[ti]['dia']))
                columna +=1

            logging.warn(lista_fechas_encabezado)


            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'Reporte.xls'})
        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'quemen_reportes.salida_productos_tienda.wizard',
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
        return self.env.ref('quemen_reportes.action_salida_productos_tienda').report_action([], data=datas)
