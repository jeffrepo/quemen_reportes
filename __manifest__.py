# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'quemen reportes',
    'version': '0.0',
    'summary': 'quemen reportes',
    'sequence':15,
    'description': """
Tienda de pasteles...
    """,
    'category':'Pasteles',
    'website': '',
    'depends': ['base','point_of_sale', 'purchase', 'sale', 'stock', 'pos_sale'],
    'data': [
    	'views/report.xml',
    	'report/producto_terminado.xml',
        # 'views/quemen_view.xml',
        'security/ir.model.access.csv',
        # 'views/salida_productos_tienda_wizard_view.xml',
        # 'views/quemen_ventas_anual_wizard_view.xml',
        # 'views/pos_config_views.xml',
        # 'views/reporte_produccion.xml',
        # 'views/reporte_productos.xml',
        # 'views/reporte_sesion.xml',
        'data/paperformat_ticket.xml',
        # 'views/informe_sesiones.xml',
        'views/reporte_ticket.xml',
        'views/informe_ticket.xml',
        # 'views/devolucion_familia_wizard_view.xml',
        # 'views/tablero_metas_wizard_view.xml',
        # 'views/reporte_descuento_wizard_view.xml',
        # 'views/reporte_ventas_wizard_view.xml',
        # 'views/reporte_ventas_piezas_wizard_view.xml',
        # 'views/reporte_metas_wizard_view.xml',
    ],
    'demo':[

    ],
    'qweb':[
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
