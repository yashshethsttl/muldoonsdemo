# -*- coding: utf-8 -*-

from odoo import models, fields


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    ocr_json = fields.Text("OCR Json Data")
