# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from uuid import uuid4
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    salida_degustacion_id = fields.Many2one('stock.picking.type', 'salida')
    
