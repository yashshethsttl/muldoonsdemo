# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_asset = fields.Boolean(string="Is Asset", default=False)
