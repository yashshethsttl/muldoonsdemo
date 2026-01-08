# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Picking(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one(
        'res.users', 'Driver', tracking=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').id)])
