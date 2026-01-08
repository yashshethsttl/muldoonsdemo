from odoo import api, fields, models


class HelpdeskStageInherit(models.Model):
    _inherit = 'helpdesk.stage'

    is_solved_stage = fields.Boolean(string='Is Solved Stage')