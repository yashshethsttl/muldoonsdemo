# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import base64


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    stock_lot_id = fields.Many2one('stock.lot')
    product_id = fields.Many2one('product.product', string='Product', related="serial_number.product_id", store=True, readonly=False)
    serial_number = fields.Many2one("stock.lot", string='Serial Number', related="equipment_id.stock_lot_id", readonly=False, store=True)
    site_name_id = fields.Many2one('res.partner', string='Site Name', related='serial_number.site_name_id', readonly=False, store=True)
    asset_id = fields.Char(string='Asset Id', related="serial_number.ref", store=True, readonly=False)
    site_address = fields.Many2one('res.partner', string='Site Address', related="serial_number.last_delivery_partner_id")
    site_id = fields.Char(string='Site Id', related="serial_number.site_id")
    signature = fields.Image('Signature', help='Signature', copy=False, attachment=True)
    sign_text = fields.Char('Auto Sign Text', default="partner_id.name")
    delivery_id = fields.Many2one('stock.picking', string='Delivery Order', readonly=True,copy=False)
    picking_id = fields.Many2one('stock.picking', string='Picking Order', readonly=True,copy=False)
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket')
    repair_order_id = fields.Many2one('repair.order', string="Repair Order")
    allow_sign = fields.Boolean(related='stage_id.allow_sign')
    final_equipment_id = fields.Many2one('maintenance.equipment', string="Equipment")

    before_maintenance_img_1 = fields.Binary(string='Before Maintenance Image 1')
    before_maintenance_img_2 = fields.Binary(string='Before Maintenance Image 2')
    after_maintenance_img_1 = fields.Binary(string='After Maintenance Image 1')
    after_maintenance_img_2 = fields.Binary(string='After Maintenance Image 2')
    time_in = fields.Datetime(string='Time In')
    time_out = fields.Datetime(string='Time Out')

    in_time = fields.Float(string='Time In')
    out_time = fields.Float(string='Time Out')

    repair_move_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='repair_id',
        string='Repair Moves',
        related='repair_order_id.move_ids',
        readonly=True
    )

    technican_note_ids = fields.One2many(
        comodel_name='maintenance.technician.notes',
        inverse_name='maintenance_request_id',
        string='Technician Notes'
    )

    maintenance_seq = fields.Char(
        string='Maintenance No.',
        readonly=True,
        copy=False,
        default=lambda self: _('New')
    )

    available_lot_ids = fields.Many2many(
        comodel_name='stock.lot',
        string='Available Assets',
        compute='_compute_available_lot_ids',
        readonly=True
    )

    is_exchange_required = fields.Boolean(
        string='Is Exchange Required',
        compute='_compute_is_exchange_required',
        store=True
    )

    partner_child_id = fields.Many2one(
        'res.partner',
        string='Contact Name',
        domain="[('parent_id', '=', site_address)]"
    )

    contact_phone = fields.Char(string='Contact Phone')

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

    equipment_status = fields.Many2one('asset.status', string='Equipment Status')

    installation_count = fields.Integer(compute='_compute_installation_count')

    def _compute_installation_count(self):
        for record in self:
            record.installation_count = self.env['stock.picking'].search_count([('maintenance_request_id', '=', record.id)])

    # @api.depends('site_address.phone', 'partner_child_id.phone', 'partner_child_id.mobile', 'site_address.mobile')
    # def _compute_partner_phone(self):
    #     for req in self:
    #         if req.partner_child_id: 
    #             if req.partner_child_id.phone:
    #                 req.contact_phone = req.partner_child_id.phone
    #             elif req.partner_child_id.mobile:
    #                 req.contact_phone = req.partner_child_id.mobile
    #         else:
    #             if req.site_address.phone:
    #                 req.contact_phone = req.site_address.phone
    #             else:
    #                 req.contact_phone = req.site_address.mobile or False


    @api.depends('stage_id')
    def _compute_is_exchange_required(self):
        for rec in self:
            rec.is_exchange_required = rec.stage_id.name == 'Exchange Required'

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


    # @api.onchange('time_in', 'time_out')
    # def _onchange_time_duration(self):
    #     for rec in self:
    #         rec.duration = 0.0
    #         if rec.time_in and rec.time_out:
    #             delta = rec.time_out - rec.time_in
    #             rec.duration = delta.total_seconds() / 3600

    @api.onchange('in_time', 'out_time')
    def _onchange_time_duration(self):
        for rec in self:
            rec.duration = 0.0
            if rec.in_time and rec.out_time:
                delta = rec.out_time - rec.in_time
                rec.duration = delta



    def consolidated_sign(self):
        first_request = self[0]
        first_parent = first_request.site_name_id.parent_id or first_request.site_name_id

        if any((request.site_name_id.parent_id or request.site_name_id) != first_parent for request in self):
            raise ValidationError("All the selected requests must belong to the same parent customer")

        if any(request.signature for request in self):
            raise ValidationError("All the selected requests must not be signed")

        if any(not request.allow_sign for request in self):
            raise ValidationError("Maintenance can be signed in allowed stage only!")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sign Maintenance Requests',
            'res_model': 'maintenance.sign.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('sttl_asset_maintenance.maintenance_sign_wizard').id,
            'target': 'new',
            'context': {'default_maintenance_request_ids': [(6, 0, self.ids)]},
        }

    def action_sign(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sign Maintenance Request',
            'res_model': 'maintenance.sign.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('sttl_asset_maintenance.maintenance_sign_wizard').id,
            'target': 'new',
            'context': {'default_maintenance_request_ids': [(6, 0, self.ids)]},
        }
    
    @api.model
    def create(self, vals):
        if vals.get('maintenance_seq', _('New')) == _('New'):
            vals['maintenance_seq'] = self.env['ir.sequence'].next_by_code(
                'maintenance.request'
            ) or _('New')
        return super().create(vals)


    def write(self, vals):
        res = super().write(vals)
        if vals.get('signature'):
            for request in self:
                request._attach_sign()

        if 'equipment_status' in vals:
            for request in self:
                if (
                    request.final_equipment_id
                    and request.final_equipment_id.stock_lot_id
                ):
                    request.final_equipment_id.stock_lot_id.asset_status_id = (
                        request.equipment_status.id
                    )
                
        for request in self:
            if request.stage_id.name != 'New Request' and not request.final_equipment_id:
                raise ValidationError(_("Please select final Equipment"))
        return res

    def _attach_sign(self):
        self.ensure_one()

        if self.site_name_id:
            message = f'Maintenance Request signed by {self.sign_text}'
        else:
            message = _('Maintenance Request signed')

        attachments = []
        if self.signature:
            # Decode from base64 to raw binary so Odoo can store it correctly
            image_binary = base64.b64decode(self.signature)
            attachments.append((
                'signature.png',  # filename
                image_binary
            ))

        self.message_post(
            body=message,
            attachments=attachments
        )
        return True

    def action_create_repair(self):
        self.ensure_one()
        picking_type = self.env['stock.picking.type'].search([
            ('warehouse_id.is_assets', '=', True),
            ('code', '=', 'repair_operation'),
            ('sequence_code','=','RO')
        ], limit=1)
        repair_vals = {
            'product_id': self.product_id.id,
            'lot_id': self.serial_number.id,
            'product_qty': 1,
            'partner_id': self.site_name_id.id
        }
        if picking_type:
            repair_vals['picking_type_id'] = picking_type.id
        repair_order_id = self.env['repair.order'].create(repair_vals)
        if repair_order_id:
            self.repair_order_id = repair_order_id.id

    def action_create_exchange(self):
        self.ensure_one()
        if self.stage_id.name != "Exchange Required" or not self.site_name_id:
            raise UserError(_(
                "You can create an exchange only when:\n"
                "- Stage is 'Exchange Required'\n"
                "- Site Name is set."
            ))
        warehouse_id = self.env['stock.warehouse'].search([('is_assets', '=', True)], limit=1)
        if warehouse_id and warehouse_id.in_type_id and self.site_name_id and self.product_id and not self.picking_id and not self.delivery_id:
            return_src_location = warehouse_id.return_type_id.default_location_src_id if warehouse_id.return_type_id else warehouse_id.in_type_id.default_location_src_id
            return_picking = self.env['stock.picking'].create({
                'partner_id': self.site_name_id.id,
                'picking_type_id': warehouse_id.return_type_id.id if warehouse_id.return_type_id else warehouse_id.in_type_id.id,
                'location_id': return_src_location.id,
                'origin': self.name,
                'user_id': self.user_id.id or self.env.user.id,
            })
            if return_picking:
                return_picking.write({
                    'move_ids_without_package': [(0, 0, {
                        'product_id': self.product_id.id,
                        'product_uom_qty': 1,
                        'location_id': return_src_location.id,
                        'name': self.name,
                        'lot_ids': self.serial_number.ids,
                    })]
                })
                self.picking_id = return_picking.id
            delivery_src_location = warehouse_id.out_type_id.default_location_src_id
            delivery_picking = self.env['stock.picking'].create({
                'partner_id': self.site_name_id.id,
                'picking_type_id': warehouse_id.out_type_id.id,
                'location_id': delivery_src_location.id,
                'origin': self.name,
                'user_id': self.user_id.id or self.env.user.id,
            })
            if delivery_picking:
                delivery_picking.write({
                    'move_ids_without_package': [(0, 0, {
                        'product_id': self.product_id.id,
                        'product_uom_qty': 1,
                        'location_id': delivery_src_location.id,
                        'name': self.name,
                    })]
                })
                self.delivery_id = delivery_picking.id

    def action_view_return_picking(self):
        self.ensure_one()
        if self.picking_id:
            return {
                'name': _('Return Picking'),
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'res_id': self.picking_id.id,
                'type': 'ir.actions.act_window',
            }
        else:
            raise ValidationError(_('No return picking found for this maintenance request.'))

    def action_view_delivery_picking(self):
        self.ensure_one()
        if self.delivery_id:
            return {
                'name': _('Delivery Order'),
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'res_id': self.delivery_id.id,
                'type': 'ir.actions.act_window',
            }
        else:
            raise ValidationError(_('No delivery order found for this maintenance request.'))

    def action_view_repairs(self):
        self.ensure_one()
        if self.repair_order_id:
            return {
                'name': _('Repair Order'),
                'view_mode': 'form',
                'res_model': 'repair.order',
                'res_id': self.repair_order_id.id,
                'type': 'ir.actions.act_window',
            }
        else:
            raise ValidationError(_('No Repair order found for this maintenance request.'))

    @api.onchange("final_equipment_id")
    def _onchange_final_equipment_id(self):
        for rec in self:
            if rec.final_equipment_id:
                rec.equipment_id = rec.final_equipment_id.id

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
    
    def action_install_equipment(self):
        self.ensure_one()
        if not self.product_id:
            raise UserError(_("Please select a product first."))
        
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)],
            limit=1
        )

        if not warehouse:
            raise UserError(_("No warehouse found for the current company."))
        
        location_id = warehouse.lot_stock_id
        if not location_id:
            raise UserError(_("No outgoing picking type found for the warehouse."))
        
        picking_type = warehouse.out_type_id
        if not picking_type:
            raise UserError(_("No outgoing picking type found for the warehouse."))


        do = self.env['stock.picking'].create({
            'partner_id': self.site_name_id.id,
            'origin': self.name,
            'location_id': location_id.id,
            'picking_type_id': picking_type.id,
            # 'location_id': picking_type.default_location_src_id.id,   # ✅ WH/Stock
            'location_dest_id': picking_type.default_location_dest_id.id,
            'maintenance_request_id': self.id,
            'move_ids_without_package': [(0, 0, {
                'product_id': self.product_id.id,
                'name': self.product_id.display_name,
                'product_uom_qty': 1,
                'product_uom': self.product_id.uom_po_id.id,
                'date': self.schedule_date or fields.Datetime.now(),
            })]
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Order'),
            'res_model': 'stock.picking',
            'res_id': do.id,
            'view_mode': 'form',
        }
    
    def action_view_installations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('maintenance_request_id', '=', self.id)],
        }