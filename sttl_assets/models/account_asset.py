# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    asset_connected = fields.Boolean(string='Asset Connected', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        assets = self.search([('name', '=', [vals['name'] for vals in vals_list])])
        if assets:
            raise ValidationError(_('Asset with the same name already exists.'))
        return super(AccountAsset, self).create(vals_list)
