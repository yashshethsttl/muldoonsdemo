# -*- coding: utf-8 -*-

from odoo import fields, models


class AssetOtherExpense(models.Model):
    _name = 'asset.other.expense'
    _description = 'Asset Other Expenses'

    title = fields.Char(string="Title")
    responsible_user_id = fields.Many2one('res.users', string="Responsible")
    total_cost = fields.Float(string="Total Cost")
    stock_lot_id = fields.Many2one("stock.lot", string="Asset")
