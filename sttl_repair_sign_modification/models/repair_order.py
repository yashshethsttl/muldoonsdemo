# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Repair(models.Model):
    _inherit = 'repair.order'

    signature = fields.Image('Signature', help='Signature', copy=False, attachment=True)
    sign_text = fields.Char('Auto Sign Text', default="partner_id.name")
    is_signed = fields.Boolean('Is Signed', compute="_compute_is_signed", store=True)
    can_sign = fields.Boolean(compute='_compute_can_sign', string='Can Sign')

    @api.depends('signature')
    def _compute_is_signed(self):
        for repair in self:
            repair.is_signed = repair.signature

    def write(self, vals):
        res = super().write(vals)
        if vals.get('signature'):
            for repair in self:
                repair._attach_sign()
        
        return res

    def _attach_sign(self):
        """ Render the delivery report in pdf and attach it to the picking in `self`. """
        self.ensure_one()
        report = self.env['ir.actions.report']._render_qweb_pdf("repair.action_report_repair_order", self.id)
        filename = "%s_signed_delivery_slip" % self.name
        if self.partner_id:
            message = _('Repair signed by %s', self.sign_text)
        else:
            message = _('Repair signed')
        self.message_post(
            attachments=[('%s.pdf' % filename, report[0])],
            body=message,
        )
        return True

    def consolidated_sign(self):
        first_order = self[0]
        first_parent = first_order.partner_id.parent_id or first_order.partner_id

        if any((order.partner_id.parent_id or order.partner_id) != first_parent for order in self):
            raise ValidationError("All the selected orders must belong to the same parent customer")

        if any(order.is_signed for order in self):
            raise ValidationError("All the selected orders must not be signed")

        if any(order.state != 'done' for order in self):
            raise ValidationError("All the selected orders must be in Repaired state")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sign Repair Orders',
            'res_model': 'repair.sign.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('sttl_repair_sign_modification.repair_sign_wizard').id,
            'target': 'new',
            'context': {'default_repair_ids': [(6, 0, self.ids)]},
        }

    def action_sign(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sign Repair Orders',
            'res_model': 'repair.sign.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('sttl_repair_sign_modification.repair_sign_wizard').id,
            'target': 'new',
            'context': {'default_repair_ids': [(6, 0, self.ids)]},
        }

    def _compute_can_sign(self):
        for rec in self:
            if rec.state not in ('done', 'under_repair', 'exchange'):
                rec.can_sign =  False
                return
            if not rec.move_ids and not (rec.internal_notes and rec.internal_notes.striptags()):
                rec.can_sign = False
                return
            rec.can_sign = True
