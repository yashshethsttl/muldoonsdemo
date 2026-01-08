from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_recurring = fields.Boolean(string="Is Recurring", default=False, copy=False)
    recurring_interval = fields.Integer(string="Recurring Interval", copy=False)
    recurring_period = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], string="Recurring Period", default='days', copy=False)
    next_recurring_date = fields.Date(
        string="Next Recurring Date",
        compute='_compute_next_recurring_date',
        store=True,
        copy=False
    )
    parent_order_id = fields.Many2one('sale.order', string='Parent Order', copy=False)
    is_recurring_copy = fields.Boolean(string='Is Recurring Copy', default=False, copy=False)
    enable_recurring_orders = fields.Boolean(
        string='Enable Recurring Orders',
        compute='_compute_enable_recurring_orders',
        store=False
    )
    
    @api.depends()
    def _compute_enable_recurring_orders(self):
        enable_recurring = self.env['ir.config_parameter'].sudo().get_param(
            'sttl_recurring_sale_order.enable_recurring_orders', False
        )
        for record in self:
            record.enable_recurring_orders = bool(enable_recurring)

    @api.model
    def default_get(self, fields_list):
        """Set default value for enable_recurring_orders from config."""
        res = super(SaleOrder, self).default_get(fields_list)
        if 'enable_recurring_orders' in fields_list:
            enable_recurring = self.env['ir.config_parameter'].sudo().get_param(
                'sttl_recurring_sale_order.enable_recurring_orders', False
            )
            res['enable_recurring_orders'] = bool(enable_recurring)
        return res

    @api.depends('is_recurring', 'recurring_interval', 'recurring_period', 'date_order', 'state')
    def _compute_next_recurring_date(self):
        for record in self:
            if record.is_recurring and record.recurring_interval and record.recurring_period:
                # Use confirmation date if order is confirmed, otherwise use order date
                if record.state in ['sale', 'done'] and record.date_order:
                    base_date = record.date_order.date()
                elif record.date_order:
                    base_date = record.date_order.date()
                else:
                    base_date = date.today()
                
                record.next_recurring_date = record._calculate_next_date(base_date)
            else:
                record.next_recurring_date = False


    def _calculate_next_date(self, base_date):
        period_map = {
            'days': {'days': self.recurring_interval},
            'weeks': {'weeks': self.recurring_interval},
            'months': {'months': self.recurring_interval},
        }
        return base_date + relativedelta(**period_map.get(self.recurring_period, {}))

    def create_recurring_order(self):
        try:
            new_order = self.copy({
                'date_order': fields.Datetime.now(),
                'is_recurring_copy': True,
                'parent_order_id': self.id,
                'origin': self.name,
            })
            # Update next recurring date for the parent order
            self.next_recurring_date = self._calculate_next_date(date.today())
            _logger.info(f"Created recurring order {new_order.name} from parent {self.name}")
            return new_order
        except Exception as e:
            _logger.error(f"Failed to create recurring order for {self.name}: {str(e)}")
            return False

    def action_view_recurring_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recurring Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('parent_order_id', '=', self.id)],
            'context': {'default_parent_order_id': self.id}
        }

    @api.model
    def process_recurring_orders(self):
        enable_recurring = self.env['ir.config_parameter'].sudo().get_param(
            'sttl_recurring_sale_order.enable_recurring_orders', False
        )
        if not enable_recurring:
            return

        today = date.today()
        recurring_orders = self.search([
            ('is_recurring', '=', True),
            ('is_recurring_copy', '=', False),
            ('next_recurring_date', '=', today),
            ('state', 'in', ['sale'])
        ])
        _logger.info(f"Processing {len(recurring_orders)} recurring orders")

        for order in recurring_orders:
            try:
                order.create_recurring_order()
            except Exception as e:
                _logger.error(f"Error processing recurring order {order.name}: {str(e)}")
                continue
