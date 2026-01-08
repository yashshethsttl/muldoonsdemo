from odoo import http
from odoo.http import content_disposition, Controller, request, route
import json


class TimeoffController(Controller):

    @http.route(['/get/timeoff_type'], type='http', auth='user', website=True)
    def get_timeoff_type(self, sortby='date', filterby='all', **kw):
        timeoff_type = request.env['hr.leave.type'].sudo().search([('id', '=', kw.get('id'))])
        return json.dumps({"request_unit": timeoff_type.request_unit})

    @http.route(['/get/timeoff_edit'], type='http', auth='user', website=True)
    def get_timeoff_type_edit(self, sortby='date', filterby='all', **kw):
        timeoff_type = request.env['hr.leave'].sudo().search([('id', '=', kw.get('id'))])
        files = {}
        if timeoff_type:
            for file in timeoff_type.supported_attachment_ids:
                data = {'id':file.id,'name':file.name}
                files[str(file.id)] = file.name
        return json.dumps(files)
    
    @http.route(['/get/timeoff_edit_remove'], type='http', auth='user', website=True)
    def get_timeoff_type_edit_remove(self, sortby='date', filterby='all', **kw):
        timeoff_attachment = request.env['ir.attachment'].sudo().search([('id', '=', kw.get('id'))])
        leave_id = request.env["hr.leave"].sudo().browse([timeoff_attachment.res_id])
        if leave_id:
            leave_id.write({
                'supported_attachment_ids':[(3, timeoff_attachment.id)]
            })
        files = {}

        return json.dumps(files)