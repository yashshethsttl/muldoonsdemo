# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ocr_qwen_api_key = fields.Char(config_parameter='sttl_purchase_ocr.ocr_qwen_api_key', string="Qwen API key")
