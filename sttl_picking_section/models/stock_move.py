# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command


class StockMove(models.Model):
    _inherit = 'stock.move'

    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False,
        help="Technical field for UX purpose."
    )
    sequence = fields.Integer(default=1)
    parent_section_id = fields.Many2one('stock.move')
    is_section_added_in_backorder = fields.Boolean(copy=False)
    is_section_added_in_dest_picking = fields.Boolean(copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('display_type') == 'line_section' or vals.get('display_type') == 'line_note':
                picking = self.env["stock.picking"].search([("id", "=", vals.get("picking_id"))])
                section_product = self.env['product.product'].search([('name', 'ilike', 'section'), ('active', '=', False)], limit=1)
                if not section_product:
                    section_product = self.env['product.product'].create({'name': 'Section', 'type': 'service', 'active': False})
                if section_product:
                    location_id = picking.location_id.id if picking else section_product.property_stock_inventory.id
                    picking_type_id = picking.picking_type_id.id if picking else False
                    vals.update({'product_id': section_product.id, 'product_uom_qty': 0, 'product_uom': section_product.uom_id.id, 'quantity': 0,
                                'location_id': location_id, "state": "confirmed", "picking_type_id": picking_type_id})
                
        res = super().create(vals_list)
        return res

    def _merge_moves(self, merge_into=False):
        return self
    
    def _prepare_procurement_values(self):
        values = super(StockMove, self)._prepare_procurement_values()
        values["sequence"] = self.sequence
        values["display_type"] = self.display_type
        return values

    def _split(self, qty, restrict_partner_id=False):
        new_move_vals = super(StockMove, self)._split(qty, restrict_partner_id)
        if new_move_vals and self.parent_section_id and not self.parent_section_id.is_section_added_in_backorder:
            parent_section_vals = {
                "name": self.parent_section_id.name,
                "display_type": self.parent_section_id.display_type,
                "sequence": self.parent_section_id.sequence,
                "location_dest_id": self.parent_section_id.location_dest_id.id,
                "picking_id": self.parent_section_id.picking_id.id
            }
            self.parent_section_id.is_section_added_in_backorder = True
            new_move_vals.append(parent_section_vals)
        return new_move_vals

    def _push_apply(self):
        new_moves = super(StockMove, self)._push_apply()
        for move in new_moves:
            if move.parent_section_id and not move.parent_section_id.is_section_added_in_dest_picking:
                move.parent_section_id.is_section_added_in_dest_picking = True
                new_section_move = self._run_push_sections(move.parent_section_id)
                if new_section_move:
                    new_section_move.picking_id = move.picking_id.id
                    new_moves |= new_section_move
        new_moves = new_moves.sudo()._action_confirm()
        return new_moves
    
    def _run_push_sections(self, section_move):
        new_section_values = {
            'picking_id': False,
        }
        new_section_move = section_move.sudo().copy(new_section_values)
        if new_section_move._skip_push():
            new_section_move.write({'location_dest_id': new_section_move.location_final_id.id})
        if new_section_move._should_bypass_reservation():
            new_section_move.write({'procure_method': 'make_to_stock'})
        if not new_section_move.location_id.should_bypass_reservation():
            section_move.write({'move_dest_ids': [(4, new_section_move.id)]})

        return new_section_move
