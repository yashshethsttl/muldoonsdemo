# -*- coding: utf-8 -*-

from odoo import models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_open_repairs(self):
        self.ensure_one()
        return {
            'name': _('Repairs'),
            'type': 'ir.actions.act_window',
            'res_model': 'repair.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_open_assets(self):
        return {
            'name': _('Assets'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'list',
            'view_id': self.env.ref('sttl_assets.view_site_report_list').id,
            'domain': [('partner_id', '=', self.id),('picking_id.state','=','done'),('product_id.is_asset','=',True),('product_uom_qty','=',1),('location_id.usage','=','customer')],
        }
