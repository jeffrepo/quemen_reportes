from odoo import api, models, fields
import logging

class ReporteProduccion(models.AbstractModel):
    _name = 'report.reporte_produccion.reporte'

    nombre_reporte=''

    def retorno_productos(self, docs):
        listado_productos_componentes={}
        listado_productos_mp = {}
        cantidad = 0
        lista_ordenes_produccion = []
        for i in docs:
            productos_general = i.move_raw_ids
            lista_ordenes_produccion+=i
            for lineas in productos_general:
                if lineas.product_id.name[0:4] == "COMP":
                    if lineas.product_id.id not in listado_productos_componentes:
                        listado_productos_componentes[lineas.product_id.id]={'nombre':lineas.product_id.name, 'id': lineas.product_id.id ,'cantidad':0, 'unidad_medida' : lineas.product_uom.name}
                    listado_productos_componentes[lineas.product_id.id]['cantidad'] += lineas.product_uom_qty
                else:
                    if lineas.product_id.id not in listado_productos_mp:
                        listado_productos_mp[lineas.product_id.id]={'nombre':lineas.product_id.name, 'id': lineas.product_id.id ,'cantidad':0, 'unidad_medida' : lineas.product_uom.name}
                    listado_productos_mp[lineas.product_id.id]['cantidad'] += lineas.product_uom_qty

        return {'lista_ordenes_produccion': lista_ordenes_produccion, 'listado_productos_componentes': listado_productos_componentes, 'listado_productos_mp': listado_productos_mp}

    def fecha_hoy(self):
        logging.warning(fields.Datetime.now())
        return fields.date.today()

    
    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': "mrp.production",
            'docs': docs,
            'retorno_productos': self.retorno_productos,
            'fecha_hoy': self.fecha_hoy,
        }
        

class ReporteProduccion1(models.AbstractModel):
    _name = 'report.quemen_reportes.reporte_produccion_productos'
    _inherit = 'report.reporte_produccion.reporte'

    nombre_reporte= 'quemen_reportes.reporte_produccion_productos'
