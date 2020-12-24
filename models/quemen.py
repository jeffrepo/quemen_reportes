# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class QuemenMetas(models.Model):
    _name = "quemen.metas"
    _description = "test"
    linea_ids = fields.One2many('quemen.metas.linea', 'meta_id', 'linea')
    tienda_almacen_id = fields.Many2one('pos.config', 'tienda')
    fecha = fields.Datetime('fecha')

class QuemenMetasLinea(models.Model):

    _name = "quemen.metas.linea"
    _description="test2"
    meta_id = fields.Many2one('quemen.metas', 'meta')
    categoria_id = fields.Many2one('categ_id', 'categoria')
    meta = fields.Float('metas')
