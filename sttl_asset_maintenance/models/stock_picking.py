# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if self.picking_type_id.warehouse_id.is_assets:
            missing_image_lines = self.move_line_ids.filtered(
                lambda line: (line.lot_id or line.lot_name) and not line.image
            )
            if missing_image_lines:
                raise UserError(_("Image is required for serial/lot numbers in asset warehouse operations. Please add images before validating."))
        
        return super().button_validate()
    

    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request')
