# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError



class SaleRequisition(models.Model):
    _name = "sale.requisition"
    _description = "Sale Requisition"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(
        string='Agreement',  required=True,  default=_('New') , readonly=True)
    active = fields.Boolean('Active', default=True)
    reference = fields.Char(string='Reference')
    order_count = fields.Integer(compute='_compute_orders_number', string='Number of Orders')
    invoice_total = fields.Monetary(compute='_compute_invoice_total', string='Total Invoiced', currency_field='currency_id')
    vendor_id = fields.Many2one('res.partner', string='Customer', check_company=True)
    requisition_type = fields.Selection([
        ('blanket_order', 'Blanket Order'), ('sale_template', 'Sale Template')],
         string='Agreement Type', required=True, default='blanket_order')
    date_start = fields.Date(string='Start Date', tracking=True)
    date_end = fields.Date(string='End Date', tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Sale Representative',
        default=lambda self: self.env.user, check_company=True)
    description = fields.Html()
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    sale_ids = fields.One2many('sale.order', 'requisition_id', string='Sale Orders')
    line_ids = fields.One2many('sale.requisition.line', 'requisition_id', string='Products to Sale', copy=True)
    product_id = fields.Many2one('product.product', related='line_ids.product_id', string='Product')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Closed'),
            ('cancel', 'Cancelled')
        ],
        string='Status', tracking=True, required=True,
        copy=False, default='draft')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True, precompute=True,
        compute='_compute_currency_id', store=True, readonly=False)
    
    @api.depends('name', 'reference')
    @api.depends_context('m2o_show_reference')
    def _compute_display_name(self):
        super()._compute_display_name()

        if not self.env.context.get('m2o_show_reference'):
            return

        for rec in self:
            if rec.reference:
                rec.display_name = f"{rec.display_name} [{rec.reference}]"
            else:
                rec.display_name = rec.name

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.requisition') or _('New')
        return super(SaleRequisition, self).create(vals)
    
    def write(self, vals):
        res = super(SaleRequisition, self).write(vals)
        # If reference field is updated
        if 'reference' in vals:
            for requisition in self:
                # Update related Sale Orders customer_order_ref
                requisition.sale_ids.write({'client_order_ref': vals['reference']})
        return res

    
    @api.depends('sale_ids.invoice_ids.amount_total', 'sale_ids.invoice_ids.state')
    def _compute_invoice_total(self):
        for requisition in self:
            total = 0.0
            for order in requisition.sale_ids:
                for invoice in order.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
                    total += invoice.amount_total
            requisition.invoice_total = total

    
    @api.depends('vendor_id')
    def _compute_currency_id(self):
        for requisition in self:
            requisition.currency_id = requisition.company_id.currency_id.id

    
    @api.depends('sale_ids')
    def _compute_orders_number(self):
        for requisition in self:
            requisition.order_count = len(requisition.sale_ids)


    def action_cancel(self):
        for requisition in self:
            for requisition_line in requisition.line_ids:
                requisition_line.supplier_info_ids.sudo().unlink()
            for order in requisition.sale_ids:
                if order.state in ['draft', 'sent']:
                    order.action_cancel()
        self.state = 'cancel'

    def action_confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You cannot confirm agreement '%(agreement)s' because it does not contain any product lines.", agreement=self.name))
        if self.requisition_type == 'blanket_order':
            for requisition_line in self.line_ids:
                if requisition_line.price_unit <= 0.0:
                    raise UserError(_('You cannot confirm a blanket order with lines missing a price.'))
                if requisition_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm a blanket order with lines missing a quantity.'))
                requisition_line._create_supplier_info()
        self.state = 'confirmed'

    def action_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def action_done(self):
        """
        Generate all sale order based on selected lines, should only be called on one agreement at a time
        """
        if any(sale_order.state in ['draft', 'sent', 'to approve'] for sale_order in self.mapped('sale_ids')):
            raise UserError(_("To close this sale requisition, cancel related Requests for Quotation.\n\n"
                "Imagine the mess if someone confirms these duplicates: double the order, double the trouble :)"))
        for requisition in self:
            for requisition_line in requisition.line_ids:
                requisition_line.supplier_info_ids.sudo().unlink()
        self.write({'state': 'done'})

    def action_view_invoices(self):
        invoices = self.sale_ids.mapped('invoice_ids')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_create_quotation(self):
        self.ensure_one()
        context = {
            'default_requisition_id': self.id,
        }
        if self.vendor_id:
            context['default_partner_id'] = self.vendor_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'context': context,
            'target': 'current',
        }
    
    def unlink(self):
        for requisition in self:
            if requisition.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete a confirmed or closed agreement.'))
        return super(SaleRequisition, self).unlink()
