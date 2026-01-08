from odoo import models, fields, api, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    json_data = fields.Text("Json Data")
