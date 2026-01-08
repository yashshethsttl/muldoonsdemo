from odoo.http import Controller, request, route


class TemplateRender(Controller):

    @route(['/get/templates'], type='json', auth="user", website=False)
    def get_templates(self):
        templates_dict = {
            "request_unit_hour": request.env['ir.ui.view'].sudo()._render_template('sttl_portal_leaves.request_unit_hour'),
            "request_unit_days": request.env['ir.ui.view'].sudo()._render_template('sttl_portal_leaves.request_unit_days'),
            "leave_duration": request.env['ir.ui.view'].sudo()._render_template('sttl_portal_leaves.leave_duration'),
            "time_selection": request.env['ir.ui.view'].sudo()._render_template('sttl_portal_leaves.time_selection'),
            "request_unit_hour_edit": request.env['ir.ui.view'].sudo()._render_template('sttl_portal_leaves.request_unit_hour_edit'),
            "request_unit_days_edit": request.env['ir.ui.view'].sudo()._render_template('sttl_portal_leaves.request_unit_days_edit'),
            "leave_duration_edit": request.env['ir.ui.view'].sudo()._render_template('sttl_portal_leaves.leave_duration_edit'),
            "time_selection_edit": request.env['ir.ui.view'].sudo()._render_template('sttl_portal_leaves.time_selection_edit'),
        }
        return templates_dict
