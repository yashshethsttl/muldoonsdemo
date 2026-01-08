from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_recurring_orders = fields.Boolean(
        string='Enable Recurring Orders',
        config_parameter='sttl_recurring_sale_order.enable_recurring_orders'
    )

    def set_values(self):
        super().set_values()
        # Update cron job active status based on setting
        cron = self.env.ref('sttl_recurring_sale_order.cron_process_recurring_orders', raise_if_not_found=False)
        if cron:
            cron.active = self.enable_recurring_orders

    @api.model
    def get_values(self):
        res = super().get_values()
        # Sync cron status with setting on load
        cron = self.env.ref('sttl_recurring_sale_order.cron_process_recurring_orders', raise_if_not_found=False)
        if cron:
            res['enable_recurring_orders'] = cron.active
        return res
