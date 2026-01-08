# -*- coding: utf-8 -*-

from odoo import models, fields


class MaintenanceStage(models.Model):
    _inherit = 'maintenance.stage'
    
    allow_sign = fields.Boolean(string="Allow Sign")
