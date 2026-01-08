# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockLot(models.Model):
    _inherit = 'stock.lot'

    account_asset_id = fields.Many2one('account.asset', string="Account Asset", ondelete="set null")
    stock_lot_image = fields.Binary("Image", store=True)

    def action_lot_open_account_assets(self):
        self.ensure_one()
        if self.account_asset_id:
            action = {
                'res_model': 'account.asset',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': self.account_asset_id.id
            }
            return action
