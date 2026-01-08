# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class RelatedAssets(models.Model):
    _name = 'related.assets'

    stock_lot_id = fields.Many2one('stock.lot', string='Stock Lot')
    product_id = fields.Many2one('product.product', string='Product')
    alert_duration_id = fields.Many2one('alert.duration', string='Alert Duration')
    maintenance_frequency_id = fields.Many2one('maintenance.frequency', string='Maintenance Frequency')
    product_lot_id = fields.Many2one('stock.lot', string='Serial No')
    asset_id = fields.Char(related='product_lot_id.ref', string='Asset Id')

    @api.onchange('product_lot_id')
    def _onchange_product_lot_id(self):
        for record in self:
            if record.product_lot_id:
                record.asset_id = record.product_lot_id.ref

    @api.model
    def create(self, vals):
        stock_lot_id = vals.get('stock_lot_id')
        product_id = vals.get('product_id')
        product_lot_id = vals.get('product_lot_id')

        existing_record = self.search([
            ('stock_lot_id', '=', stock_lot_id),
            ('product_id', '=', product_id),
            ('product_lot_id', '=', product_lot_id)
        ], limit=1)

        if existing_record:
            raise ValidationError(_('Product already exists with the same serial number.'))
        res = super(RelatedAssets, self).create(vals)
        res.create_maintenace_request()
        return res
    
    def create_maintenace_request(self):
        for rec in self:
            if rec.maintenance_frequency_id and rec.stock_lot_id.installation_date:
                scheduled_date = rec.get_maintenance_scheduled_date()
                self.env['maintenance.request'].create({
                    'name': rec.product_id.name + " (" + rec.maintenance_frequency_id.name + " maintenance)",
                    'product_id': rec.stock_lot_id.product_id.id if rec.stock_lot_id.product_id else False,
                    'maintenance_type': 'preventive',
                    'serial_number': rec.stock_lot_id.id if rec.stock_lot_id else False,
                    'asset_id': rec.stock_lot_id.ref,
                    'schedule_date': scheduled_date,
                    'stock_lot_id': rec.stock_lot_id.id if rec.stock_lot_id else False,
                    'recurring_maintenance': True,
                    'repeat_interval': rec.maintenance_frequency_id.frequency,
                    'repeat_unit': rec.maintenance_frequency_id.frequency_type,
                    'equipment_id': rec.stock_lot_id.maintenance_equipment_id.id if rec.stock_lot_id else False,
                    'site_id': rec.stock_lot_id.site_id if rec.stock_lot_id.site_id else False,
                    'site_name_id': rec.stock_lot_id.site_name_id.id if rec.stock_lot_id.site_name_id else rec.stock_lot_id.last_delivery_partner_id.id
                })

    def write(self, vals):
        for record in self:
            stock_lot_id = vals.get('stock_lot_id', record.stock_lot_id.id)
            product_id = vals.get('product_id', record.product_id.id)
            product_lot_id = vals.get('product_lot_id', record.product_lot_id.id)

            existing_record = self.search([
                ('stock_lot_id', '=', stock_lot_id),
                ('product_id', '=', product_id),
                ('product_lot_id', '=', product_lot_id),
                ('id', '!=', record.id)
            ], limit=1)

            if existing_record:
                raise ValidationError(_('Product already exists with the same serial number.'))
            res = super(RelatedAssets, self).write(vals)
            if vals.get('maintenance_frequency_id'):
                self.create_maintenace_request()
        return res

    def get_maintenance_scheduled_date(self):
        for rec in self:
            maintenance_scheduled_date = False
            freq = rec.maintenance_frequency_id.frequency or 0
            freq_type = rec.maintenance_frequency_id.frequency_type
            installation_date = rec.stock_lot_id.installation_date

            if installation_date:
                if freq_type == 'day':
                    maintenance_scheduled_date = installation_date + relativedelta(days=freq)
                elif freq_type == 'week':
                    maintenance_scheduled_date = installation_date + relativedelta(weeks=freq)
                elif freq_type == 'month':
                    maintenance_scheduled_date = installation_date + relativedelta(months=freq)
                elif freq_type == 'year':
                    maintenance_scheduled_date = installation_date + relativedelta(years=freq)

            return maintenance_scheduled_date
