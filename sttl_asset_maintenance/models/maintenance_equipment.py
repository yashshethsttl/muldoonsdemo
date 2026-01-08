# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.osv import expression


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
    product_id = fields.Many2one('product.product', string="Product", related="stock_lot_id.product_id", store=True, readonly=False)
    stock_lot_id = fields.Many2one('stock.lot', string="Serial Number")
    customer_id = fields.Many2one("res.partner", string="Customer", related="stock_lot_id.last_delivery_partner_id", readonly=False, store=True)
    location_id = fields.Many2one("stock.location", string="Location", related="stock_lot_id.location_id")
    location_usage = fields.Selection(related="location_id.usage", string="Location Type")
    current_location = fields.Char(string='Current Address', related="stock_lot_id.current_location")


    @api.depends('name', 'stock_lot_id.ref', 'stock_lot_id.name')
    def _compute_display_name(self):
        for rec in self:
            parts = []

            if rec.stock_lot_id and rec.stock_lot_id.ref:
                parts.append(rec.stock_lot_id.ref)

            if rec.stock_lot_id and rec.stock_lot_id.name:
                parts.append(rec.stock_lot_id.name)

            if rec.product_id and rec.product_id.name:
                parts.append(rec.product_id.name)

            rec.display_name = " - ".join(parts) if parts else rec.name or ""


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        if name:
            domain = expression.OR([
                [('name', operator, name)],
                [('stock_lot_id.name', operator, name)],
                [('stock_lot_id.ref', operator, name)],
                [('product_id.name', operator, name)],
            ])
            args = expression.AND([args, domain])

        return super().name_search(name='', args=args, operator=operator, limit=limit)
