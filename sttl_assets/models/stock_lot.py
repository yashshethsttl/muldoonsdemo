# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockLot(models.Model):
    _inherit = 'stock.lot'

    related_assets_ids = fields.One2many('related.assets', 'stock_lot_id', string='Related Assets')
    is_asset = fields.Boolean(string='Is Asset', default=False)
    site_id = fields.Char(compute="_compute_site_data", string='Site Id', store=True)
    account_asset_id = fields.Many2one('account.asset', string="Account Asset", ondelete="set null")
    stock_lot_image = fields.Binary("Image", store=True)
    asset_model_id = fields.Many2one(related='account_asset_id.model_id', string='Asset Model')
    asset_group_id = fields.Many2one(related='account_asset_id.asset_group_id', string='Asset Group')
    last_delivery_partner_id_copy = fields.Many2one("res.partner", compute="_compute_site_data", store=True, string="Site Address")
    site_name_id = fields.Many2one("res.partner", string='Site Name', compute="_compute_site_data", store=True)
    total_repair_count = fields.Integer('Total Repair Count', compute="_compute_total_repair_count")
    location_name = fields.Char(related='location_id.complete_name')
    location_usage = fields.Selection(related="location_id.usage")
    current_location = fields.Char(string='Current Location', compute='_compute_current_location_id', store=True)
    asset_repair_expense_ids = fields.One2many('asset.repair.expense', 'stock_lot_id', string="Asset Repair Expenses", compute="_compute_repair_expenses")
    asset_other_expense_ids = fields.One2many('asset.other.expense', 'stock_lot_id', string="Other Expenses")
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_asset_cost")
    total_repair_cost = fields.Float(string="Total Repair Cost", compute="_compute_total_asset_cost")
    total_other_cost = fields.Float(string="Total Other Cost", compute="_compute_total_asset_cost")
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")
    installation_date = fields.Date(string="Installation Date", compute="_compute_installation_date", readonly=False, store=True)

    @api.depends('location_id')
    def _compute_installation_date(self):
        for rec in self:
            if rec.location_id and rec.location_id.warehouse_id and rec.location_id.warehouse_id.is_assets:
                rec.installation_date = False

    @api.depends('asset_repair_expense_ids', 'asset_other_expense_ids')
    def _compute_total_asset_cost(self):
        for rec in self:
            total_repair_cost = 0
            total_other_cost = 0
            for repair_expense in rec.asset_repair_expense_ids:
                total_repair_cost += repair_expense.total_cost
            for other_expense in rec.asset_other_expense_ids:
                total_other_cost += other_expense.total_cost

            rec.total_repair_cost = total_repair_cost
            rec.total_other_cost = total_other_cost
            rec.total_cost = total_repair_cost + total_other_cost

    def _compute_repair_expenses(self):
        for rec in self:
            repair_orders = self.env['repair.order'].search(
                [('lot_id', '=', rec.id), ('state', 'in', ('done', 'exchange_planned', 'exchange'))],
                order='id asc'
            )
            
            if not repair_orders:
                rec.asset_repair_expense_ids = False
                continue

            vals_list = []
            for repair in repair_orders:
                vals_list.append({
                    "title": repair.name,
                    "responsible_user_id": repair.user_id.id,
                    "total_cost": repair.total_cost,
                    "stock_lot_id": rec.id,
                })

            repair_expenses = self.env['asset.repair.expense'].create(vals_list)

            rec.asset_repair_expense_ids = [(6, 0, repair_expenses.ids)]

    @api.depends('location_id')
    def _compute_current_location_id(self):
        for record in self:
            if record.location_id and record.location_id.complete_name == 'Partners/Customers':
                record.current_location = record.last_delivery_partner_id.complete_name if record.last_delivery_partner_id.complete_name else record.last_delivery_partner_id.name
            elif record.location_id and record.location_id.complete_name != 'Partners/Customers':
                record.current_location = record.location_id.complete_name if record.location_id.complete_name else record.location_id.name

    def _compute_total_repair_count(self):
        for rec in self:
            rec.total_repair_count = self.env['repair.order'].search_count([('lot_id', '=', rec.id)])

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockLot, self).create(vals_list)
        if res.account_asset_id:
            res.account_asset_id.write({'asset_connected': True})
        return res

    @api.depends('last_delivery_partner_id', 'last_delivery_partner_id.parent_id', 'last_delivery_partner_id.ref', 'last_delivery_partner_id.parent_id.ref')
    def _compute_site_data(self):
        for record in self:
            record.site_id = (
                record.last_delivery_partner_id.parent_id.ref
                if record.last_delivery_partner_id and record.last_delivery_partner_id.parent_id
                else record.last_delivery_partner_id.ref
                if record.last_delivery_partner_id
                else False
            )
            record.site_name_id = record.last_delivery_partner_id.parent_id.id
            record.last_delivery_partner_id_copy = record.last_delivery_partner_id.id

    def unlink(self):
        for record in self:
            if record.account_asset_id:
                record.account_asset_id.write({'asset_connected': False})
        return super(StockLot, self).unlink()
            
    def write(self, vals):
        for record in self:
            if 'account_asset_id' in vals.keys() and vals.get('account_asset_id'):
                new_asset = self.env['account.asset'].browse(vals['account_asset_id'])
                new_asset.write({'asset_connected': True})
                if record.account_asset_id:
                    record.account_asset_id.write({'asset_connected': False})
            elif 'account_asset_id' in vals.keys():
                if record.account_asset_id:
                    record.account_asset_id.write({'asset_connected': False})
        return super(StockLot, self).write(vals)

    def action_lot_open_account_assets(self):
        self.ensure_one()
        if self.account_asset_id:
            action = {
                'res_model': 'account.asset',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': self.account_asset_id.id
            }
            return action

    def open_field_service(self):
        self.ensure_one()
        return {
            'name': _('Field Service'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('product_lot_id', '=', self.id)],
            'context': {'default_product_lot_id': self.id},
        }

    def action_lot_open_repairs(self):
        action = super().action_lot_open_repairs()
        action['context'].update(
            {'default_partner_id': self.last_delivery_partner_id.id if self.last_delivery_partner_id else False})
        return action
