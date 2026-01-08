# -*- coding: utf-8 -*-

from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    maintenance = fields.Boolean(string="Maintenance", default=False)
