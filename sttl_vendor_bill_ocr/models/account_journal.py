from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _create_document_from_attachment(self, attachment_ids=None):

        attachments = self.env['ir.attachment'].browse(attachment_ids)
        if not attachments:
            raise UserError(_("No attachment was provided"))

        invoices = self.env['account.move']
        for attachment in attachments:
            self.env['account.move'].action_ocr_resume(attachment)
            invoice = self.env['account.move'].action_save(attachment)
            if invoice:
                invoices += invoice
        return invoices