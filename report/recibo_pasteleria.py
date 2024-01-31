# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ReportRecibo(models.AbstractModel):
    _name ='report.recibo_pasteleria.recibo'

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        self.model = 'hr.payslip'
        docs = self.env[self.model].browse(docids)

        return {
        'doc_ids': docids,
        'doc_model': self.model,
        'docs': docs,
        }
