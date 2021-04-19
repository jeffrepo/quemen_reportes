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
        'views/quemen_view.xml',
        'views/salida_productos_tienda_wizard_view.xml',
        'views/quemen_ventas_anual_wizard_view.xml',
        'views/pos_config_views.xml',
        'views/reporte_produccion.xml',
        'views/reporte_productos.xml'

    ],
    'demo':[

    ],
    'qweb':[
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
