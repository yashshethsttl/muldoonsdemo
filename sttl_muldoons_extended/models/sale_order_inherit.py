from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Selection(
        [('call_in', 'Call-In'), ('hostesses', 'Hostesses'), ('std_order_ocs', 'Standard Order(OCS)')],
        string='Order Type',
    )


# class SaleOrderLineInherit(models.Model):
#     _inherit = 'sale.order.line'

#     qty_available = fields.Float(
#         string='Quantity Available',
#         related='product_id.qty_available',
#         store=True,
#     )