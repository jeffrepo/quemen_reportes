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
    'depends': ['base','point_of_sale'],
    'data': [
        # 'views/pastelera_views.xml',
        'views/salida_productos_tienda_wizard_view.xml',
    ],
    'demo':[

    ],
    'qweb':[
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
