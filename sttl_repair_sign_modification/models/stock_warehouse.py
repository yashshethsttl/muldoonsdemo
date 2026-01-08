# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_assets = fields.Boolean(
        string='Is Assets',
    )
    return_type_id = fields.Many2one(
        'stock.picking.type',
        string='Return Type',
    )
