# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_reserved_qty(self):
        for line in self:
            # Get stock moves related to this sale order line   
            reserved_qty = 0
            stock_moves = self.env['stock.move'].search([
                ('sale_line_id', '=', line.id),  # Only consider moves that are reserved (assigned)
            ])
            if stock_moves:
                stock_moves_line = self.env['stock.move.line'].search([
                    ('move_id', 'in', stock_moves[0].ids),  # Only consider moves that are reserved (assigned)
                ])
                if stock_moves_line:
                    reserved_qty = stock_moves_line[0].quantity
            return reserved_qty
