# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AlertDuration(models.Model):
    _name = 'alert.duration'

    name = fields.Char(string='Name')
    duration = fields.Integer(string='Duration')
    duration_type = fields.Selection([('day', 'Days'), ('week', 'Weeks'), ('month', 'Months')], string='Duration Type')
