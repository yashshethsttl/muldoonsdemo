from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = 'repair.order'
    
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_repair_cost")

    @api.depends('move_ids.product_id')
    def _compute_total_repair_cost(self):
        for rec in self:
            total_cost = 0
            for move in rec.move_ids.filtered(lambda r : r.repair_line_type == "add"):
                if move.product_id and move.product_id.standard_price:
                    total_cost += (move.product_id.standard_price * move.quantity)

            rec.total_cost = total_cost

    @api.depends('product_id', 'company_id', 'picking_id', 'picking_id.move_ids', 'picking_id.move_ids.lot_ids', 'partner_id')
    def _compute_allowed_lot_ids(self):
        super()._compute_allowed_lot_ids()
        for repair in self:
            if not repair.partner_id or not repair.allowed_lot_ids:
                continue

            lots = self.env['stock.lot'].browse(repair.allowed_lot_ids.ids).with_context(prefetch_fields=False)
            filtered_lots = lots.filtered(lambda lot: lot.last_delivery_partner_id.id == repair.partner_id.id)
            repair.allowed_lot_ids = filtered_lots
