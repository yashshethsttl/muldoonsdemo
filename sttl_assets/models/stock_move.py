# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    site_id = fields.Char(string='Site Id', compute='_compute_site_id', store=True)
    parent_id = fields.Many2one('res.partner', string='Parent', store=True, compute='_compute_parent_id')

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.ref', 'partner_id.parent_id.ref')
    def _compute_site_id(self):
        for record in self:
            record.site_id = record.partner_id.parent_id.ref or record.partner_id.ref

    @api.depends('partner_id', 'partner_id.parent_id')
    def _compute_parent_id(self):
        for record in self:
            record.parent_id = record.partner_id.parent_id.id if record.partner_id.parent_id else record.partner_id.id if record.partner_id else False

    def open_move_history(self):
        action = self.env.ref('sttl_assets.stock_move_line_action_assets').read()[0]

        # Safely evaluate the existing domain or default to an empty list
        existing_domain = eval(action.get('domain') or '[]')

        # Build the extra domain using picking_id.partner_id
        extra_domain = ['|'] * (len(self) - 1)  # Add OR conditions for multiple records
        for rec in self:
            extra_domain += [
                ('picking_partner_id', '=', rec.partner_id.id),
                ('product_id', '=', rec.product_id.id)
            ]

        # Combine the domains
        action['domain'] = existing_domain + extra_domain
        return action

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    site_name_id = fields.Many2one(related='picking_partner_id.parent_id', string='Site Name')
