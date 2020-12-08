# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict
import logging
import xlsxwriter
import io
import base64
# import win32com.client as win32

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


            # set_column(first_col, last_col, width, cell_format, options)

            if w.consolidado_tienda==1:
                listado_tiendas=[]
                lista_conceptos=[]
                lista_categoria=[]
                lista_tiendas={}
                transferencias_filtradas=[]
                productos_filtrados=[]

                s=", "
                hoja.write(2, 2, 'Consolidado por Tienda')
                # hoja.write(2, 3, w.consolidado_tienda[0])
                hoja.write(6, 2, 'Tienda: ')

                # inventario = self.env['stock.picking'].search([('picking_type_id', 'in', w.tipo_salida_ids.ids)])
                # logging.warn(inventario)
                logging.warn('Prueba Tiendas')
                for tienda in w.tienda_ids:
                    # lista_tiendas.append({'nombre_tienda' : tienda.name, 'id' : tienda.id , 'cantidad_productos' : 0})
                    if tienda.id not in lista_tiendas:
                        lista_tiendas[tienda.id] =  {'nombre_tienda' : tienda.name, 'id' : tienda.id , 'cantidad_productos' : 0}

                logging.warn(lista_tiendas)

                hoja.write(7, 2, 'Concepto:')

                for concepto in w.tipo_salida_ids:
                    lista_conceptos.append(concepto.name)
                    # logging.warn(concepto)

                hoja.write(7, 5, str(s.join(lista_conceptos)))


                hoja.write(8, 2, 'Familia: ')
                # hoja.write(8, 3, str(lista_tiendas=', '.join(w.categoria_ids)))

                for categoria in w.categoria_ids:
                    lista_categoria.append(categoria.name)
                    # logging.warn(categoria)

                hoja.write(8, 5, str(s.join(lista_categoria)))

                transferencias = self.env['stock.picking'].search([('picking_type_id','in', w.tipo_salida_ids.ids),
                ('scheduled_date','>=',str(w.fecha_inicio)),('scheduled_date','<=',str(w.fecha_final)), ('state', '=', 'done')])

                listado_productos={}

                for transferencia in transferencias:
                    total=0
                    for linea in transferencia.move_ids_without_package:
                        if linea.product_id.id not in listado_productos:
                            listado_productos[linea.product_id.id] = {'nombre_producto': linea.product_id.name, 'codigo': linea.product_id.default_code, 'tiendas': lista_tiendas}

                        listado_productos[linea.product_id.id]['tiendas'][transferencia.picking_type_id.warehouse_id.id]['cantidad_productos'] = linea.product_uom_qty
                logging.warn(listado_productos)
                        # for tienda in listado_productos[linea.product_id.id]['tiendas']:
                        #     logging.warn(transferencia)
                        #     logging.warn(tienda)
                        #     logging.warn(linea.product_uom_qty)
                        #     if int(transferencia.picking_type_id.warehouse_id.id) == int(tienda['id']):
                        #         total += linea.product_uom_qty
                        #         tienda['cantidad_productos'] += linea.product_uom_qty



                # logging.warn(listado_productos)

                # el siguiente codigo despues de "aux" hasta logging.warn(result) obtiene los objetos repetidos de una lista y en que posicion se encuentran
                # aux = defaultdict(list)
                # for index , item in enumerate(productos_filtrados):
                #     aux[item].append(index)
                # result = {item: indexs for item, indexs in aux.items() if len(indexs) > 1}
                # logging.warn(result)

                productos_filtrados1 = list(set(productos_filtrados))

                hoja.write(9, 2, 'Fecha Inicio:')
                hoja.write(9, 3, w.fecha_inicio, formato_fecha)
                hoja.write(9, 5, w.fecha_final, formato_fecha)
                hoja.write(13, 2, 'Clave')
                hoja.write(13, 3, 'Descripcion')
                fila=14
                fila1=13
                columna=2
                columna1=3
                # columna2=4
                columna_tiendas=4
                for store1 in lista_tiendas:
                    hoja.write(13, columna_tiendas, str(store1['nombre_tienda']) )
                    columna_tiendas += 1


                for clave in listado_productos:
                    hoja.write(fila, columna, str(listado_productos[clave]['codigo']))
                    hoja.write(fila, columna1, str(listado_productos[clave]['nombre_producto']))
                    columna_cantidad = 4

                    for store in listado_productos[clave]['tiendas']:
                        # hoja.write(fila1, columna3, str(store['nombre_tienda']))
                        hoja.write(fila, columna_cantidad, str(store['cantidad_productos']))
                        columna_cantidad += 1
                        # # hoja.write(filas, columnas, str(store['cantidad_productos']))
                        # filas = filas +1
                    fila = fila + 1
                    # logging.warn(str(clave) + ' -->' + str(listado_productos[clave]['codigo']))




            if w.consolidado_dia==1:
                lista_tiendas=[]
                lista_categoria=[]
                lista_conceptos=[]
                hoja.write(1, 2, 'Consolidado por día')
                # hoja.write(1, 3, w.consolidado_dia)
                hoja.write(3, 5, 'Reporte de salida de productos por día')
                hoja.write(4, 2, 'Tienda: ')

                for tienda in w.tienda_ids:
                    listado_tiendas.append(tienda.name)

                s=", "

                hoja.write(4, 5, str(s.join(listado_tiendas)))
                hoja.write(5, 2, 'Concepto:')

                for concepto in w.tipo_salida_ids:
                    lista_conceptos.append(concepto.name)

                hoja.write(5, 5, str(s.join(lista_conceptos)))


                hoja.write(6, 2, 'Familia')

                for categoria in w.categoria_ids:
                    lista_categoria.append(categoria.name)

                hoja.write(6, 5, str(s.join(lista_categoria)))
                hoja.write(7, 2, 'Fecha inicio')
                hoja.write(7, 3, w.fecha_inicio, formato_fecha)
                hoja.write(7, 5, w.fecha_final, formato_fecha)
                hoja.write(9, 2, 'Clave')
                hoja.write(9, 3, 'Descripcion')
                hoja.write(10, 4, 'Lunes')
                hoja.write(10, 5, 'Martes')
                hoja.write(10, 6, 'Miercoles')
                hoja.write(10, 7, 'Jueves')
                hoja.write(10, 8, 'Viernes')
                hoja.write(10, 9, 'Sabado')
                hoja.write(10, 10, 'Domingo')
                hoja.write(10, 11, 'Lunes')
                hoja.write(9, 12, 'CANTIDAD')
                hoja.write(9, 13, 'SUBTOTAL')
                hoja.write(9, 14, 'IMPORTE')




            # hoja.set_colum(9, 2, width)
            # hoja.Columns.AutoFit()

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
