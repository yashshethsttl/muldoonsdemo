# -*- coding: utf-8 -*-

from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if rec.display_type == 'line_section' or rec.display_type == 'line_note':
                section_product = self.env['product.product'].search([('name', 'ilike', 'section'), ('active', '=', False)], limit=1)
                if not section_product:
                    section_product = self.env['product.product'].create({'name': 'Section', 'type': 'service', 'active': False})
                if section_product:
                    sale_order = rec.order_id
                    picking_ids = sale_order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
                    for picking in picking_ids:
                        self.env['stock.move'].create({'name': rec.name, 'picking_id': picking.id, "display_type": rec.display_type, 'sequence': rec.sequence})
        return res

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.display_type == 'line_section' or rec.display_type == 'line_note':
                moves = self.env['stock.move'].search([('sale_line_id', '=', rec.id), ('state', 'not in', ['cancel', 'done'])])
                for move in moves:
                    move.name = rec.name
        return res
    
    def has_valued_move_ids(self):
        res = super().has_valued_move_ids()
        if res and type(res) != bool:
            updated_moves = []
            for move in res:
                if move.display_type not in ('line_section', 'line_note'):
                    updated_moves.append(move)
            return updated_moves
        else:
            res
