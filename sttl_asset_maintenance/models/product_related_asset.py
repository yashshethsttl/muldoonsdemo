# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductRelatedAsset(models.Model):
    _name = 'product.related.asset'
    _description = "Product Related Asset"

    parent_asset_id = fields.Many2one('product.template', string="Parent Asset")
    product_id = fields.Many2one('product.product', string="Product")

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        related_vals = []
        for rec in res:
            last_related_asset_line = self.search(
                [('parent_asset_id', '=', rec.parent_asset_id.id), ('id', 'not in', res.ids)],
                order='create_date desc',
                limit=1
            )
            lots_domain = [('product_id', '=', rec.parent_asset_id.id)]
            if last_related_asset_line:
                lots_domain.append(('create_date', '>=' , last_related_asset_line.create_date))
            lots = self.env['stock.lot'].search(lots_domain)
            for lot in lots:
                related_vals.append({
                    'stock_lot_id': lot.id,
                    'product_id': rec.product_id.id,
                })
        if related_vals:
            self.env['related.assets'].create(related_vals)

        return res

