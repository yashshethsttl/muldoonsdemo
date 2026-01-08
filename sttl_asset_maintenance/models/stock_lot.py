# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockLot(models.Model):
    _inherit = 'stock.lot'

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', string="Equipment")
    maintenance_request_count = fields.Integer(
        string="Maintenance Requests",
        compute="_compute_maintenance_request_count"
    )
    asset_status_id = fields.Many2one("asset.status", string="Asset Status")

    @api.model_create_multi
    def create(self, vals_list):
        lots = super().create(vals_list)
        for rec in lots:
            if rec.product_id.is_asset:
                asset_name = rec.name
                if rec.ref:
                    asset_name = f"{rec.name} ({rec.ref})"
                equipment_id = self.env['maintenance.equipment'].create({
                    "name": asset_name,
                    "stock_lot_id": rec.id,
                    "serial_no": rec.name
                })
                if equipment_id:
                    rec.maintenance_equipment_id = equipment_id.id
            rec.create_related_assets()
        return lots

    @api.onchange("ref")
    def _onchange_ref(self):
        for rec in self:
            if rec.maintenance_equipment_id:
                if rec.ref:
                    rec.maintenance_equipment_id.name = f"{rec.name} ({rec.ref})"
                else:
                    rec.maintenance_equipment_id.name = rec.name

    def create_related_assets(self):
        "Add related assets that are already linked with the product."
        related_assets = self.env['product.related.asset'].search([('parent_asset_id', '=', self.product_id.product_tmpl_id.id)])
        vals_list = []
        for related_asset in related_assets:
            vals_list.append({
                "product_id": related_asset.product_id.id,
                "stock_lot_id": self.id
            })
        if vals_list:
            self.env["related.assets"].create(vals_list)

    def action_lot_open_equipment(self):
        self.ensure_one()
        if self.maintenance_equipment_id:
            action = {
                'res_model': 'maintenance.equipment',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': self.maintenance_equipment_id.id
            }
            return action
        else:
            raise ValidationError("No equipment found for the asset")

    def action_lot_open_maintenance_requests(self):
        self.ensure_one()
        domain = ['|', ('stock_lot_id', '=', self.id),('equipment_id', '=', self.maintenance_equipment_id.id)]
        return {
            'name': _('Maintenance Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'default_equipment_id': self.maintenance_equipment_id.id if self.maintenance_equipment_id else False,
                'default_stock_lot_id': self.id,
                'default_serial_number': self.id,
                'default_product_id': self.product_id.id,
            },
        }

    def write(self, vals):
        if vals.get('stock_lot_image') and self.stock_lot_image:
            attachment = self.env['ir.attachment'].create({
                'name': 'image.jpg',
                'type': 'binary',
                'datas': self.stock_lot_image,
                'res_model': 'stock.lot',
                'res_id': self.id, 
            })
            if attachment:
                self.message_post(
                    body=_('Asset image updated'),
                    attachment_ids=attachment.ids,
                )
        
        return super(StockLot, self).write(vals)

    @api.depends('maintenance_equipment_id')
    def _compute_maintenance_request_count(self):
        for lot in self:
            domain = ['|', ('stock_lot_id', '=', lot.id),('equipment_id', '=', lot.maintenance_equipment_id.id)]
            lot.maintenance_request_count = self.env['maintenance.request'].search_count(domain)

    @api.depends_context('wizard_show_asset')
    @api.depends('name', 'ref')
    def _compute_display_name(self):
        if not self.env.context.get('wizard_show_asset'):
            return super(StockLot, self)._compute_display_name()

        for rec in self:
            if rec.name and rec.ref:
                rec.display_name = f"{rec.name} ({rec.ref})"
            else:
                rec.display_name = rec.name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = list(args or [])
        if name:
            domain = ['|', ('name', operator, name), ('ref', operator, name)]
            args = domain + args

        return super(StockLot, self).name_search(name='', args=args, operator=operator, limit=limit)
