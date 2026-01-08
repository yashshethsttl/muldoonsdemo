# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    image = fields.Binary(string="Image", copy=False)
    is_asset_warehouse = fields.Boolean(compute='_compute_is_asset_warehouse', store=False)

    @api.depends('picking_type_id.warehouse_id','picking_type_id.warehouse_id.is_assets')
    def _compute_is_asset_warehouse(self):
        for line in self:
            line.is_asset_warehouse = line.picking_type_id.warehouse_id.is_assets if line.picking_type_id.warehouse_id else False

    def write(self, vals):
        res = super().write(vals)
        
        if 'lot_id' in vals:
            for line in self:
                if line.image and line.lot_id:
                    line.lot_id.write({
                        'stock_lot_image': line.image
                    })
                    
        if 'image' in vals:
            for line in self:
                if line.lot_id:
                    line.lot_id.write({
                        'stock_lot_image': line.image
                    })
        return res
