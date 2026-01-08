from odoo import models, fields, api


class StockReturnPickingInherit(models.TransientModel):
    _inherit = 'stock.return.picking'

    allowed_stock_lot_ids = fields.Many2many(
        comodel_name='stock.lot',
        relation='stock_return_picking_allowed_lot_rel',
        column1='wizard_id',
        column2='lot_id',
        string='Allowed Stock Lots',
        related='ticket_id.allowed_stock_lot_ids', readonly=True
    )    

class StockReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    asset_ids = fields.Many2many(
        comodel_name='stock.lot',
        relation='stock_return_line_asset_rel',
        column1='line_id',
        column2='lot_id',
        string='Assets',
        related='wizard_id.ticket_id.asset_ids', readonly=True
    )
