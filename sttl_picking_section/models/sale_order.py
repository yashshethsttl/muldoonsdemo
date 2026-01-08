# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            section_lines = rec.order_line.filtered(lambda x: x.display_type == 'line_section' or x.display_type == 'line_note')
            for line in section_lines:
                picking_ids = rec.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
                for picking in picking_ids:
                    move = self.env['stock.move'].create({'name': line.name, 'picking_id': picking.id, "display_type": line.display_type, 'sequence': line.sequence})
        return res
