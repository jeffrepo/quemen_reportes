from odoo import models, fields, api
from collections import defaultdict
import logging
import xlsxwriter
import io
import base64
import dateutil.parser
import datetime

class VentasAnuales(models.TransientModel):
    _name = 'quemen_reportes.quemen_ventas_anual.wizard'
    _description = "Reporte para pasteleria "

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_final = fields.Date('Fecha final')
    categoria_ids = fields.Many2many('product.category','quemen_reportes_categoria_rela', string="Categoria")
    tienda_ids = fields.Many2many('pos.config','quemen_reporte_ventas_anual_tiendas_rel',string="Tiendas")
    name = fields.Char('File Name', size=32)
    archivo = fields.Binary('Archivo')

    def generar_excel(self):

        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
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
            logging.warn(pedidosAtras)
            listado_categorias={}
            listado_productos={}
            productos=[]
            totalImporte=0
            ventasTotales=0
            cumplidoCategoria=0
            totalPzas=0
            totPzasAñoP=0
            tp=0
            totalMeta=0
            sumaVentas=0
            fecha1=w.fecha_final
            fechaFinal=fecha1.strftime('%d,%m,%Y')
            for pedido in pedidos:
                unaFecha=pedido.date_order
                fechaPedido=unaFecha.strftime('%d,%m,%Y')
                añoActual=unaFecha.strftime('%Y')
                if pedido.config_id.id in w.tienda_ids.ids:
                    for lineas in pedido.lines:
                        if lineas.product_id.categ_id.id not in listado_categorias:
                            listado_categorias[lineas.product_id.categ_id.id]={'nombre_categoria': lineas.product_id.categ_id.name, 'productos':[], 'totalImporte':0, 'metas':0, 'cumplidoCategoria':0,'totalPzas':0, 'ventasTotales':0, 'totPzasAñoP':0}
                            metas = self.env['quemen.metas'].search([('fecha','>=',str(w.fecha_inicio)),('fecha','<=',str(w.fecha_final))])
                            for meta in metas:
                                if meta.tienda_almacen_id.id in w.tienda_ids.ids:
                                    for lin in meta.linea_ids:
                                        if lin.categoria_id.id == lineas.product_id.categ_id.id:
                                            if lin.categoria_id not in listado_categorias:
                                                listado_categorias[lineas.product_id.categ_id.id]['metas']=lin.metaTotal
                                                # listado_categorias[lineas.product_id.categ_id.id]['totalMeta']+=lin.metaTotal
                        listado_categorias[lineas.product_id.categ_id.id]['totalImporte']+=round(lineas.price_subtotal_incl, 2)
                        listado_categorias[lineas.product_id.categ_id.id]['cumplidoCategoria']=round((listado_categorias[lineas.product_id.categ_id.id]['totalImporte']/listado_categorias[lineas.product_id.categ_id.id]['metas'])*100,2)
                    listado_categorias[lineas.product_id.categ_id.id]['productos'].append({'nombre':lineas.product_id.name, 'piezas': lineas.qty, 'monto': pedido.amount_total})
                    if fechaPedido == fechaFinal:
                        sumaVentas+=lineas.price_subtotal_incl
                    listado_categorias[lineas.product_id.categ_id.id]['ventasTotales']=round(sumaVentas,2)
                    listado_categorias[lineas.product_id.categ_id.id]['totalPzas']+=lineas.qty
            for pedidosA in pedidosAtras:
                if pedidosA.config_id.id in w.tienda_ids.ids:
                    for lineas1 in pedidosA.lines:
                        tp+=lineas1.qty
                        # listado_categorias[lineas1.product_id.categ_id.id]={'totPzasAñoP':0}
                        listado_categorias[lineas1.product_id.categ_id.id]['totPzasAñoP']=tp

            logging.warn(listado_categorias)
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
