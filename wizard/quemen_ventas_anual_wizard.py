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

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_final = fields.Date('Fecha final')
    categoria_ids = fields.Many2many('product.category','quemen_reportes_categoria_rela', string="Categoria")
    tienda_ids = fields.Many2many('pos.config','quemen_reporte_ventas_anual_tiendas_rel',string="Tiendas")
    name = fields.Char('File Name', size=32)
    archivo = fields.Binary('Archivo')
    locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8"))

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
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]={'categoria_padre': lineas.product_id.categ_id.parent_id.name, 'categorias_hijas':{}, 'totPzasPadr': 0, 'totalImpPdre':0, 'totalMtaPdre':0, 'totalcumplPdre':0, 'pzasPadreAñoPasado': 0,'totVtasAñoPdre':0, 'totVtasAñoPasadoPadre': 0, 'incrementoPadre': 0, 'costoTotalPadre': 0, 'porcentajeCostoTotalPadre':0}
                            if lineas.product_id.categ_id.id not in listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas']:
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]={'nombre': lineas.product_id.categ_id.name, 'productosh':{}, 'totalImporte':0, 'metas': 0, 'cumplidoCategoria':0, 'totalPzas':0, 'ventasTotales':0, 'totPzasAñoP':0, 'totVtasAñoP':0, 'incremento':0, 'costoTotal':0, 'porcentajeCostoTotal': 0}
                                for met in metas:
                                    if met.tienda_almacen_id.id in w.tienda_ids.ids:
                                        for lin in met.linea_ids:
                                            if lin.categoria_id.id == lineas.product_id.categ_id.id:
                                                if lin.categoria_id not in listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas']:
                                                    listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['metas']=lin.metaTotal
                                                    listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalMtaPdre']+=lin.metaTotal
                                #
                                # for degustaciones in degustacion:
                                #     if
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]={'nombre':lineas.product_id.name, 'piezas': 0, 'monto':0}
                            if fechaPedido == fechaFinal:
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['piezas']+=lineas.qty
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['monto']+=round(lineas.price_subtotal_incl,2)
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['totalPzas']+=lineas.qty
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['totalImporte']+=round(listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['monto'],2)

                            if listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['metas'] <= 0:
                                print("No hay meta")
                            if listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['metas'] > 0:
                                listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['cumplidoCategoria']=round((listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['totalImporte']/listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['metas'])*100,2)
                            fincremento=lineas.qty*lineas.product_id.standard_price
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['costoTotal']+=fincremento
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['ventasTotales']+=round(lineas.price_subtotal_incl,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['porcentajeCostoTotal']=round((listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['costoTotal']/listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['ventasTotales'])*100,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totPzasPadr']+=round(listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['piezas'],2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalImpPdre']+=round(listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas.product_id.categ_id.id]['productosh'][lineas.product_id.id]['monto'],2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totVtasAñoPdre']+=round(lineas.price_subtotal_incl,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalcumplPdre']=round((listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalImpPdre']/listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totalMtaPdre'])*100,2)
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['costoTotalPadre']+=fincremento
                            listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['porcentajeCostoTotalPadre']=round((listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['costoTotalPadre']/listado_categoria_padre[lineas.product_id.categ_id.parent_id.id]['totVtasAñoPdre'])*100,2)


            incrementoPadre=0

            for pedidosA in pedidosAtras:
                if pedidosA.config_id.id in w.tienda_ids.ids:
                    for lineas1 in pedidosA.lines:
                        logging.warn(lineas1.product_id.categ_id.id)
                        logging.warn(lineas1.product_id.categ_id.name)
                        logging.warn(lineas1.product_id.name)
                        if lineas1.product_id.categ_id.parent_id.id in listado_categoria_padre and lineas1.product_id.categ_id.id in listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas']:
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['totPzasAñoP']+=lineas1.qty
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['totVtasAñoP']+=lineas1.price_subtotal_incl
                            calculoIncre=round((listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['ventasTotales']/(listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['totVtasAñoP']-1))*100,2)
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['incremento']=round(calculoIncre,2)
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['totVtasAñoPasadoPadre']+=lineas1.price_subtotal_incl
                            incrementoPadre=round((listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['totVtasAñoPdre']/(listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['totVtasAñoPasadoPadre']-1))*100,2)
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['incrementoPadre']=round(incrementoPadre,2)
                            # if lineas1.product_id.categ_id.id in listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas']:
                            #     listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['categorias_hijas'][lineas1.product_id.categ_id.id]['productosh'][lineas1.product_id.id]['piezasAñoPasado']+=lineas1.qty
                            listado_categoria_padre[lineas1.product_id.categ_id.parent_id.id]['pzasPadreAñoPasado']+=lineas1.qty



            logging.warn('Listado categoria padre')
            logging.warn(listado_categoria_padre)

            hoja.write(2,1, 'Linea Quemen')

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


            hoja.write(4,1, 'Descripción Corta')
            hoja.write(4,2, 'Piezas')
            hoja.write(4,3, 'Importe')
            hoja.write(4,4, 'Meta')
            hoja.write(4,5, '%Cumplido')
            años=fecha1.strftime('%Y')
            hoja.write(4,6, 'Ventas ' +str(años))
            hoja.write(4,7, 'VTA PZAS ' +str(atras1))
            hoja.write(4,8, 'VENTA ' +str(atras1))
            hoja.write(4,9, 'INCREMENTO')
            hoja.write(4,10, 'Costo Total')
            hoja.write(4,11, '% Costo Total')
            hoja.write(4,12, 'DESGUS')
            hoja.write(4,13, 'DEVO')
            hoja.write(4,14, '%DEVO')
            fila1=5
            for cate in listado_categoria_padre:
                for catehija in listado_categoria_padre[cate]['categorias_hijas']:
                    hoja.write(fila1, 1, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['nombre']))
                    hoja.write(fila1, 2, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['totalPzas']))
                    hoja.write(fila1, 3, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['totalImporte']))
                    hoja.write(fila1, 4, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['metas']))
                    hoja.write(fila1, 5, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['cumplidoCategoria']))
                    hoja.write(fila1, 6, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['ventasTotales']))
                    hoja.write(fila1, 7, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['totPzasAñoP']))
                    hoja.write(fila1, 8, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['totVtasAñoP']))
                    hoja.write(fila1, 9, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['incremento']))
                    hoja.write(fila1, 10, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['costoTotal']))
                    hoja.write(fila1, 11, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['porcentajeCostoTotal']))
                    fila1+=1
                    for prod in listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh']:
                        hoja.write(fila1, 1, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['nombre']))
                        hoja.write(fila1, 2, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['piezas']))
                        hoja.write(fila1, 3, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['monto']))
                        # hoja.write(fila1, 7, str(listado_categoria_padre[cate]['categorias_hijas'][catehija]['productosh'][prod]['piezasAñoPasado']))
                        fila1+=1
                hoja.write(fila1, 1, 'SUBTOTAL '+str(listado_categoria_padre[cate]['categoria_padre']))
                hoja.write(fila1, 2, str(listado_categoria_padre[cate]['totPzasPadr']))
                hoja.write(fila1, 3, str(listado_categoria_padre[cate]['totalImpPdre']))
                hoja.write(fila1, 4, str(listado_categoria_padre[cate]['totalMtaPdre']))
                hoja.write(fila1, 5, str(listado_categoria_padre[cate]['totalcumplPdre']))
                hoja.write(fila1, 6, str(listado_categoria_padre[cate]['totVtasAñoPdre']))
                hoja.write(fila1, 7, str(listado_categoria_padre[cate]['pzasPadreAñoPasado']))
                hoja.write(fila1, 8, str(listado_categoria_padre[cate]['totVtasAñoPasadoPadre']))
                hoja.write(fila1, 9, str(listado_categoria_padre[cate]['incrementoPadre']))
                hoja.write(fila1, 10, str(listado_categoria_padre[cate]['costoTotalPadre']))
                hoja.write(fila1, 11, str(listado_categoria_padre[cate]['porcentajeCostoTotalPadre']))
                fila1+=1



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
