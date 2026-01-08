# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Task(models.Model):
    _inherit = 'project.task'

    # stock_lot_id = fields.Many2one('stock.lot', string='Stock Lot')
    product_id = fields.Many2one('product.product', string='Product')
    product_lot_id = fields.Many2one('stock.lot', string='Serial No')
    asset_id = fields.Char(related="product_lot_id.ref", string='Asset Id')
    site_id = fields.Char(string='Site Id',related="product_lot_id.site_id")
    site_address = fields.Many2one('res.partner', string='Site Address',related="product_lot_id.last_delivery_partner_id")
