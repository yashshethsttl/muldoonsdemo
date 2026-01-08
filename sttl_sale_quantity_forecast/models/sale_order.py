# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner(self):
        for rec in self:
            rec.pricelist_id = rec.partner_id.property_product_pricelist
            rec.sale_order_template_id = rec.partner_id.quotation_template_id
