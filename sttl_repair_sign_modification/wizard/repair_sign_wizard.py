# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RepairSignWizard(models.TransientModel):
    _name = 'repair.sign.wizard'
    _description = 'Repair Sign Wizard'

    repair_ids = fields.Many2many('repair.order', string='Repairs')
    sign_text = fields.Char('Auto Sign Text', compute="_compute_sign_text", inverse="_set_sign_text", store=True)
    partner_id = fields.Many2one('res.partner', string="Customer", compute="_compute_partner_id", store=True)
    signature = fields.Binary('Signature', required=True)
    is_sign_text_manual = fields.Boolean(default=False)

    def action_confirm_signature(self):
        for record in self.repair_ids:
            record.write({
                'signature': self.signature,
                'is_signed': True,
                'sign_text': self.sign_text
            })
        return {'type': 'ir.actions.act_window_close'}

    @api.depends('repair_ids')
    def _compute_partner_id(self):
        for wizard in self:
            if wizard.repair_ids:
                wizard.partner_id = wizard.repair_ids[0].partner_id.parent_id.id or wizard.repair_ids[0].partner_id.id

    @api.depends('partner_id')
    def _compute_sign_text(self):
        for wizard in self:
            if not wizard.is_sign_text_manual:
                wizard.sign_text = wizard.partner_id.name if wizard.partner_id else ''

    def _set_sign_text(self):
        for wizard in self:
            wizard.is_sign_text_manual = True
