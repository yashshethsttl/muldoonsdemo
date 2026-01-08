# -*- coding: utf-8 -*-

from odoo import fields, models


class AssetStatus(models.Model):
    _name = 'asset.status'
    _description = "Asset Status"

    name = fields.Char()
