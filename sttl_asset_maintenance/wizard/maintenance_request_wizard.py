# -*- coding: utf-8 -*-
 
from odoo import fields, models, _

 
class MaintenanceRequestWizard(models.TransientModel):
    _name = 'maintenance.request.wizard'
    _description = 'Maintenance Request Wizard'
    
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    asset_ids = fields.Many2many(
        comodel_name='stock.lot',
        relation='maintenance_wizard_asset_stock_lot_rel',
        column1='wizard_id',                              
        column2='lot_id',
        string='Asset ID',
        required=True
    )
    allowed_product_ids = fields.Many2many("product.product")
    allowed_stock_lot_ids = fields.Many2many(
        comodel_name='stock.lot',
        relation='maintenance_wizard_allowed_stock_lot_rel',
        column1='wizard_id',
        column2='lot_id',
        string='Allowed Stock Lots'
    )

    def create_maintenance_request(self):
        vals_list = []
        for asset in self.asset_ids:
            vals_list.append({
                'name': f'Maintenance for {asset.name}',
                'serial_number': asset.id,
                'product_id': self.product_id.id,
                'asset_id': asset.name,
                'site_name_id': self.helpdesk_ticket_id.partner_id.id,
                'equipment_id': asset.maintenance_equipment_id.id if asset.maintenance_equipment_id else False
            })

        maintenance_request_ids = self.env['maintenance.request'].create(vals_list)
        return {
            'name': _('Maintenance Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'list,form',
            'domain': [('id', 'in', maintenance_request_ids.ids)],
        }
