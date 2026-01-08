# -*- coding: utf-8 -*-

from odoo import models, fields


class HrContract(models.Model):
    _inherit = "hr.contract"

    rrsp_company = fields.Monetary("RRSP Company", currency_field='currency_id')
    fam_serv_gov = fields.Monetary(string="Fam Serv/Gov", currency_field='currency_id')
