# -*- coding: utf-8 -*-

from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False,
        help="Technical field for UX purpose.",
        related='move_id.display_type',
    )
