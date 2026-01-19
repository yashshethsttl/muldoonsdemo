from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Selection(
        [('call_in', 'Call-In'), ('hostesses', 'Hostesses'), ('std_order_ocs', 'Standard Order(OCS)')],
        string='Order Type',
    )

    sale_order_template_id = fields.Many2one(
        comodel_name='sale.order.template',
        string="Quotation Template",
        compute='_compute_sale_order_template_id',
        store=True,
        readonly=False,
        check_company=True,
        precompute=True,
        domain="""[
            '|', ('company_id', '=', False), ('company_id', '=', company_id),
            '|', ('partner_id', '=', False), ('partner_id', '=', partner_id)
        ]"""
    )