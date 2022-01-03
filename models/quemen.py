# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class QuemenMetas(models.Model):
    _name = "quemen.metas"
    _description = "Metas de pos quemen"

    linea_ids = fields.One2many('quemen.metas.linea', 'meta_id', 'linea')
    tienda_almacen_id = fields.Many2one('pos.config', 'Tienda')
    fecha_inicio = fields.Date('Fecha inicio')
    fecha_final = fields.Date('Fecha Final')

class QuemenMetasLinea(models.Model):
    _name = "quemen.metas.linea"
    _description="lineas de metas pos quemen"

    meta_id = fields.Many2one('quemen.metas', 'Meta')
    categoria_id = fields.Many2one('product.category', 'Categoria')
    metaTotal = fields.Float('metas')
