# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from collections import defaultdict


class SaleRequisitionLine(models.Model):
    _name = "sale.requisition.line"
    _inherit = 'analytic.mixin'
    _description = "Sale Requisition Line"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], required=True)

    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        compute='_compute_product_uom_id', store=True, readonly=False, precompute=True,
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure')
    product_description_variants = fields.Char('Description')
    price_unit = fields.Float(string='Unit Price', related = "product_id.list_price", required=True,readonly=False,store=True)
    qty_ordered = fields.Float(compute='_compute_ordered_qty', string='Ordered')
    requisition_id = fields.Many2one('sale.requisition', required=True, string='Sale Agreement', ondelete='cascade')
    company_id = fields.Many2one('res.company', related='requisition_id.company_id', string='Company', store=True, readonly=True)
    supplier_info_ids = fields.One2many('product.supplierinfo', 'sale_requisition_line_id')
    amount_total = fields.Float(compute='_compute_amount_total', string='Amount', store=True)

    @api.depends('product_id', 'product_qty', 'price_unit')
    def _compute_amount_total(self):
        for line in self:
            line.amount_total = line.price_unit * line.product_qty

    def _create_supplier_info(self):
        self.ensure_one()
        sale_requisition = self.requisition_id
        if sale_requisition.requisition_type == 'blanket_order' and sale_requisition.vendor_id:
            # create a supplier_info only in case of blanket order
            self.env['product.supplierinfo'].sudo().create({
                'partner_id': sale_requisition.vendor_id.id,
                'product_id': self.product_id.id,
                'product_tmpl_id': self.product_id.product_tmpl_id.id,
                'price': self.price_unit,
                'currency_id': self.requisition_id.currency_id.id,
                'sale_requisition_line_id': self.id,
            })

    @api.depends('product_id')
    def _compute_product_uom_id(self):
        for line in self:
            line.product_uom_id = line.product_id.uom_id

    @api.depends('requisition_id.sale_ids.state', 'requisition_id.sale_ids.order_line.product_uom_qty')
    def _compute_ordered_qty(self):
        for line in self:
            total = 0.0
            # Include both 'draft' and 'confirmed' sale orders
            for po in line.requisition_id.sale_ids.filtered(lambda sale_order: sale_order.state in ['draft', 'sale', 'done']):
                for po_line in po.order_line.filtered(lambda order_line: order_line.product_id == line.product_id):
                    if po_line.product_uom != line.product_uom_id:
                        total += po_line.product_uom._compute_quantity(po_line.product_uom_qty, line.product_uom_id)
                    else:
                        total += po_line.product_uom_qty
            line.qty_ordered = total
