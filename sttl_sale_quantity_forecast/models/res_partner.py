# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    quotation_template_id = fields.Many2one('sale.order.template', 'Quotation Template')
