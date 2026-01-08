# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Frequency(models.Model):
    _name = 'maintenance.frequency'

    name = fields.Char(string='Name')
    frequency = fields.Integer(string='Frequency', default=1)
    frequency_type = fields.Selection(
        [
        ('day', 'Days'),
        ('week', 'Weeks'),
        ('month', 'Months'),
        ('year', 'Years'),
    ], string='Frequency Type', default='day')
