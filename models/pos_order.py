# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from uuid import uuid4
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'
    fecha_hora_prueba = fields.Datetime(string='Fecha hora prueba')

    def devolucion_acumulado(self, salida_degustacion, fecha_inicio, fecha_final):
        logging.warn("Prueba de ")

        salidas_degustaciones=self.env['stock.picking'].search([('picking_type_id','=',salida_degustacion),('scheduled_date','>=',str(fecha_inicio_hora)),('scheduled_date','<=',str(fecha_final_hora))])
        logging.warn(salidas_degustaciones)
        return True
