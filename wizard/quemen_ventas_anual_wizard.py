from odoo import models, fields, api
from collections import defaultdict

class VentasAnuales(models.TransientModel):
    _name = 'quemen_reportes.quemen_ventas_anual.wizard'
    _description = "Reporte para pasteleria "

    fecha_inicio = fields.Datetime('Fecha inicio')
    fecha_final = fields.Datetime('Fecha final')
    categoria_ids = fields.Many2many('product.category','quemen_reportes_categoria_rel',string="Categoria")
    name = fields.Char('File Name', size=32)
    archivo = fields.Binary('Archivo')


    def generar_excel(self):

        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')

            merge_format = libro.add_format({'align': 'center'})



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
