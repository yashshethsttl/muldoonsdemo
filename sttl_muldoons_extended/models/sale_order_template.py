from odoo import models, fields


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )