# -*- coding: utf-8 -*-
 
from odoo import fields, models, api, _
from odoo.exceptions import UserError
 
 
class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    team_maintenance = fields.Boolean(related='team_id.maintenance', readonly=True)
    maintenance_count = fields.Integer(compute='_compute_maintenance_count')
    
    product_id = fields.Many2one('product.product', string='Product')
    asset_ids = fields.Many2many(
        comodel_name='stock.lot',
        relation='helpdesk_ticket_asset_stock_lot_rel',
        string='Asset ID',
    )
    schedule_date = fields.Datetime(string='Schedule Date')
    allowed_product_ids = fields.Many2many("product.product")
    allowed_stock_lot_ids = fields.Many2many(
        comodel_name='stock.lot',
        relation='helpdesk_ticket_allowed_stock_lot_rel',
        string='Allowed Stock Lots'
    )
    contact_name = fields.Char(string='Contact Name')

    image_1 = fields.Binary(string='Image 1')
    image_2 = fields.Binary(string='Image 2')

    partner_child_id = fields.Many2one(
        'res.partner',
        string='Contact Name',
        domain="[('parent_id', '=', partner_id)]"
    )

    request_type = fields.Selection([
        ('installation', 'Installation'),
        ('removal', 'Removal'),
        ('co2_tank_replacement', 'CO2 Tank Replacement'),
        ('service_call', 'Services Call'),
        ('white_glove', 'White Glove and/or Top Ups'),
        ('filter_change', 'Filter Change'),
        ('exchange', 'Exchange'),
        ('others', 'Others')
    ], string='Request Type')

    filtered_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_filtered_product_ids',
        store=False
    )

    @api.depends('request_type', 'allowed_product_ids')
    def _compute_filtered_product_ids(self):
        for rec in self:
            if rec.request_type == 'installation':
                rec.filtered_product_ids = self.env['product.product'].search([('is_asset', '=', True)])
            else:
                rec.filtered_product_ids = rec.allowed_product_ids.filtered(
                    lambda p: p.is_asset
                )

    available_lot_ids = fields.Many2many(
        comodel_name='stock.lot',
        string='Available Assets',
        compute='_compute_available_lot_ids',
        readonly=True
    )


    @api.depends('product_id')
    def _compute_available_lot_ids(self):
        StockLot = self.env['stock.lot']
        for rec in self:
            if not rec.product_id:
                rec.available_lot_ids = [(5, 0, 0)]
                continue

            lots = StockLot.search([
                ('product_id', '=', rec.product_id.id),
                ('location_id.usage', '!=', 'customer'),
                ('product_qty', '>', 0),
            ])

            rec.available_lot_ids = [(6, 0, lots.ids)]

    @api.depends('partner_id.phone', 'partner_child_id.phone', 'partner_child_id.mobile', 'partner_id.mobile')
    def _compute_partner_phone(self):
        for ticket in self:
            if ticket.partner_child_id: 
                if ticket.partner_child_id.phone:
                    ticket.partner_phone = ticket.partner_child_id.phone
                elif ticket.partner_child_id.mobile:
                    ticket.partner_phone = ticket.partner_child_id.mobile
            else:
                if ticket.partner_id.phone:
                    ticket.partner_phone = ticket.partner_id.phone
                else:
                    ticket.partner_phone = ticket.partner_id.mobile or False

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.partner_child_id = False

    @api.onchange('partner_id')
    def _onchange_partner_id_update_allowed_products(self):
        StockLot = self.env["stock.lot"]
        domain = []
        if self.partner_id:
            domain = [
                '|',
                ('last_delivery_partner_id_copy', '=', self.partner_id.id),
                ('site_name_id', '=', self.partner_id.id)
            ]

        partner_assets = StockLot.search(domain)
        allowed_products = partner_assets.product_id.ids
        partner_asset_ids = partner_assets.ids

        self.allowed_product_ids = [(6, 0, allowed_products)]
        self.allowed_stock_lot_ids = [(6, 0, partner_asset_ids)]
    
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = self.env['maintenance.request'].search_count([('helpdesk_ticket_id', '=', record.id)])
    
    def action_create_maintenance(self):
        self.ensure_one()
        assets = self.asset_ids or [False]

        vals_list = []

        for asset in assets:
            vals_list.append({
                'name': f'Maintenance for {asset.name}' if asset else f'Maintenance for {self.name}',
                'serial_number': asset.id if asset else False,
                'product_id': self.product_id.id if self.product_id else False,
                'asset_id': asset.name if asset else False,
                'site_name_id': self.partner_id.id if self.partner_id else False,
                'equipment_id': asset.maintenance_equipment_id.id if asset and asset.maintenance_equipment_id else False,
                'helpdesk_ticket_id': self.id,
                'schedule_date': self.schedule_date,
                'before_maintenance_img_1': self.image_1,
                'before_maintenance_img_2': self.image_2,
                'user_id': self.user_id.id,
                'instruction_text': self.description,
                'partner_child_id': self.partner_child_id.id if self.partner_child_id else False,
                'contact_phone': self.partner_phone,
                'request_type': self.request_type,
                'site_name_id': self.partner_id.id if self.partner_id else False,
            })
        maintenance_request_ids = self.env['maintenance.request'].create(vals_list)
        return {
            'name': _('Maintenance Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'list,form',
            'domain': [('id', 'in', maintenance_request_ids.ids)],
        }

    def action_view_maintenance_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'res_model': 'maintenance.request',
            'view_mode': 'list,form',
            'domain': [('helpdesk_ticket_id', '=', self.id)],
        }
    

    def action_view_maintenance(self):
        self.ensure_one()
        maintenance = self.env['maintenance.request'].search(
            [('helpdesk_ticket_id', '=', self.id)],
            limit=1
        )

        if not maintenance:
            return False
        
        return {
            'name': 'Maintenance Request',
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'res_id': maintenance.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'create': False,
            }
        }

    def action_purchase_new_machine(self):  
        self.ensure_one()
        if not self.product_id:
            raise UserError(_("Please select a product first."))

        seller = self.product_id.seller_ids[:1]
        if not seller:
            raise UserError(_("No vendor defined on the selected product."))

        vendor = seller.partner_id

        po = self.env['purchase.order'].create({
            'partner_id': vendor.id,
            'origin': self.name,
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'name': self.product_id.display_name,
                'product_qty': 1,
                'product_uom': self.product_id.uom_po_id.id,
                'price_unit': seller.price,
                'date_planned': fields.Datetime.now(),
            })]
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Order'),
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
        }
    

    @api.model
    def write(self, vals):
        res = super().write(vals)

        if 'stage_id' in vals:
            solved_stages = self.env['helpdesk.stage'].search([
                ('is_solved_stage', '=', True)
            ]).ids

            if not solved_stages:
                return res

            solved_tickets = self.filtered(lambda t: t.stage_id.id in solved_stages)

            if not solved_tickets:
                return res
            
            Stage = self.env['maintenance.stage']

            repaired_stage = self.env['maintenance.stage'].search([
                ('name', '=', 'Repaired')
            ], limit=1)

            if not repaired_stage:
                return res

            maintenances = self.env['maintenance.request'].search([
                ('helpdesk_ticket_id', 'in', solved_tickets.ids),
                ('stage_id.name', '!=', 'Scrap'),
            ])
            
            if maintenances:
                maintenances.write({'stage_id': repaired_stage.id})

        return res