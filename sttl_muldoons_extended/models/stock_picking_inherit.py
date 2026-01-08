from odoo import fields, models, api


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    salesperson_id = fields.Many2one("res.users", string="Salesperson", related='sale_id.user_id', store=True)