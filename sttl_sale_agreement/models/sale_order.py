from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    requisition_id = fields.Many2one(
        'sale.requisition', 
        string='Agreement', 
        copy=False,
    )
    requisition_type = fields.Selection(related='requisition_id.requisition_type')
    
    def action_create_sales_orders(self):
        """Confirm selected quotations and create sales orders."""
        for order in self:
            if order.state in ('draft', 'sent'):  # quotation stage
                order.action_confirm()

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        # if cleared, remove only lines linked to any agreement
        self.client_order_ref = self.requisition_id.reference
        self.order_line = [(3, line.id) for line in self.order_line if line.requisition_line_id]

        # Remove only lines that belong to the *previous* agreement
        self.order_line = [
            (4, line.id) for line in self.order_line
            if line.requisition_line_id
        ]

        if not self.sale_order_template_id:
            # Add new lines for the currently selected agreement
            order_lines = []
            for line in self.requisition_id.line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'price_unit': line.price_unit,
                    'name': line.product_id.display_name,
                    'requisition_line_id': line.id,
                }
                if self.requisition_type == 'sale_template':
                    vals['product_uom_qty'] = line.product_qty
                else:
                    vals['product_uom_qty'] = 0.0

                order_lines.append((0, 0, vals))

            if order_lines:
                self.order_line = [(4, l.id) for l in self.order_line if l.id] + order_lines


    def action_view_agreement(self):
        if not self.requisition_id:
            return {'type': 'ir.actions.act_window_close'}
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Agreement',
            'res_model': 'sale.requisition',
            'view_mode': 'form',
            'res_id': self.requisition_id.id,
            'target': 'current',
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    requisition_line_id = fields.Many2one(
        'sale.requisition.line',
        string="Agreement Line",
        copy=False,
        store=True
    )
