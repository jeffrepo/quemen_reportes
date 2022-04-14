from odoo import api, models
import logging

class ReporteProduccion(models.AbstractModel):
    _name = 'report.reporte_produccion.reporte'

    nombre_reporte=''

    def retorno_productos(self, docs):
        listado_productos={}
        cantidad = 0
        lista_ordenes_produccion = []

        for i in docs:
            productos_general = i.move_raw_ids
            lista_ordenes_produccion+=i
            for lineas in productos_general:
                if lineas.product_id.id not in listado_productos:
                    listado_productos[lineas.product_id.id]={'nombre':lineas.product_id.name, 'id': lineas.product_id.id ,'cantidad':0, 'unidad_medida' : lineas.product_uom.name}
                listado_productos[lineas.product_id.id]['cantidad'] += lineas.product_uom_qty

        return {'lista_ordenes_produccion': lista_ordenes_produccion, 'listado_productos': listado_productos}



    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.production'
        docs = self.env[self.model].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'retorno_productos': self.retorno_productos
        }

class ReporteProduccion1(models.AbstractModel):
    _name = 'report.quemen_reportes.reporte_produccion_productos'
    _inherit = 'report.reporte_produccion.reporte'

    nombre_reporte= 'quemen_reportes.reporte_produccion_productos'
