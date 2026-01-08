# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    related_asset_ids = fields.One2many('product.related.asset', 'parent_asset_id', string="Related Assets")

