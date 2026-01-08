from odoo import models
 
 
class StockPicking(models.Model):
    _inherit = 'stock.picking'
 
    def action_next_transfer(self):
        res = super().action_next_transfer()
        for picking in self._get_next_transfers():
            picking.driver_id = self.driver_id
            picking.user_id = self.user_id
        return res
