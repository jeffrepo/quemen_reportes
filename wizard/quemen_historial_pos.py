from odoo import models, fields, api
from collections import defaultdict
import logging
import xlsxwriter
import io
import base64
import dateutil.parser
import datetime


class Historial(models.TransientModel):
    _name = 'quemen.historial_pos'
    _description = "Reporte para pasteleria historial"

    punto_venta = fields.Many2one('pos.config', 'Punto de venta')
    fecha_inicio = fields.Date('Fecha')
    linea_ids = fields.One2many('quemen.historial_pos.lineas', 'historial_id', 'lineas')
    

class HistorialLineas(models.TransientModel):
    _name = 'quemen.historial_pos.lineas'
    _description='test'

    categoria_id = fields.Many2one('product.category', 'Categoria')
    historial_id = fields.Many2one('quemen.historial_pos', 'Historial')
    piezas = fields.Float('Piezas')
    ventas = fields.Float('Venta')
