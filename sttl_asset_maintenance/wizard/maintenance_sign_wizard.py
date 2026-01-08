# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceSignWizard(models.TransientModel):
    _name = 'maintenance.sign.wizard'
    _description = 'Maintenance Sign Wizard'

    maintenance_request_ids = fields.Many2many('maintenance.request', string='Maintenance Requests')
    sign_text = fields.Char('Auto Sign Text', compute="_compute_sign_text", inverse="_set_sign_text", store=True)
    partner_id = fields.Many2one('res.partner', string="Customer", compute="_compute_partner_id", store=True)
    signature = fields.Binary('Signature', required=True)
    is_sign_text_manual = fields.Boolean(default=False)

    def action_confirm_signature(self):
        self.ensure_one()
        for record in self.maintenance_request_ids:
            record.write({
                'signature': self.signature,
                'sign_text': self.sign_text
            })
        return {'type': 'ir.actions.act_window_close'}

    @api.depends('maintenance_request_ids')
    def _compute_partner_id(self):
        for wizard in self:
            if wizard.maintenance_request_ids:
                wizard.partner_id = wizard.maintenance_request_ids[0].site_name_id.parent_id.id or wizard.maintenance_request_ids[0].site_name_id.id

    @api.depends('partner_id')
    def _compute_sign_text(self):
        for wizard in self:
            if not wizard.is_sign_text_manual:
                wizard.sign_text = wizard.partner_id.name if wizard.partner_id else ''

    def _set_sign_text(self):
        for wizard in self:
            wizard.is_sign_text_manual = True
