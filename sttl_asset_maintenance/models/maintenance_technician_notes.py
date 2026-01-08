from odoo import models, fields


class MaintenanceTechnicianNotes(models.Model):
    _name = 'maintenance.technician.notes'
    _description = 'Maintenance Technician Notes'

    date = fields.Date(string='Date', default=fields.Date.context_today)
    technician_id = fields.Many2one('hr.employee', string='Technician', default=lambda self: self.env.user.employee_id.id)
    action = fields.Text(string='Action')
    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request')