# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons.stock.report.stock_traceability import autoIncrement
from odoo.tools import format_datetime


class MrpStockReport(models.TransientModel):
    _inherit = 'stock.traceability.report'

    def _get_main_lines_assets(self):
        context = dict(self.env.context)
        return self.with_context(context).get_lines_asset()

    @api.model
    def get_main_lines_assets(self, given_context=None):
        res = self.search([('create_uid', '=', self.env.uid)], limit=1)
        if not res:
            return self.create({}).with_context(given_context)._get_main_lines_assets()
        return res.with_context(given_context)._get_main_lines_assets()

    @api.model
    def get_lines_asset(self, line_id=False, **kw):
        context = dict(self.env.context)
        model = kw and kw['model_name'] or context.get('model')
        rec_id = kw and kw['model_id'] or context.get('active_id')
        level = kw and kw['level'] or 1
        lines = self.env['stock.move.line']
        move_line = self.env['stock.move.line']
        if rec_id and model == 'stock.lot':
            lines = move_line.search([
                ('lot_id', '=', context.get('lot_name') or rec_id),
                ('state', '=', 'done'),
            ])
        elif rec_id and model == 'stock.move.line' and context.get('lot_name'):
            record = self.env[model].browse(rec_id)
            dummy, is_used = self._get_linked_move_lines(record)
            if is_used:
                lines = is_used
        elif rec_id and model in ('stock.picking', 'mrp.production'):
            record = self.env[model].browse(rec_id)
            if model == 'stock.picking':
                lines = record.move_ids.move_line_ids.filtered(lambda m: m.lot_id and m.state == 'done')
            else:
                lines = record.move_finished_ids.mapped('move_line_ids').filtered(lambda m: m.state == 'done')
        move_line_vals = self._lines(line_id, model_id=rec_id, model=model, level=level, move_lines=lines)
        lot_id = self.env['stock.lot'].browse(rec_id)
        final_vals = sorted(move_line_vals, key=lambda v: v['date'], reverse=True)
        if final_vals:
            for i in final_vals:
                picking = self.env['stock.picking'].search(
                    [
                        ("name", '=', i.get('reference_id'))
                    ])
                if picking and picking.sale_id:
                    i.update({
                        'customer': picking.sale_id.partner_id.name,
                    })
                if lot_id and lot_id.last_delivery_partner_id:
                    i.update({
                        'site_id': lot_id.last_delivery_partner_id.ref,
                    })
                    i.update({
                        'location': lot_id.last_delivery_partner_id.name,
                    })
        lines = self._final_vals_to_lines_assets(final_vals, level)
        return lines

    @api.model
    def _final_vals_to_lines_assets(self, final_vals, level):
        lines = []
        for data in final_vals:
            lines.append({
                'id': autoIncrement(),
                'model': data['model'],
                'model_id': data['model_id'],
                'parent_id': data['parent_id'],
                'usage': data.get('usage', False),
                'is_used': data.get('is_used', False),
                'lot_name': data.get('lot_name', False),
                'lot_id': data.get('lot_id', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            data.get('lot_name', False),
                            format_datetime(self.env, data.get('date', False), tz=False, dt_format=False),
                            data.get('location_source', False),
                            data.get('location_destination', False),
                            data.get('customer', ''),
                            data.get('site_id', ''),
                            data.get('location', ''),
                            ],
                'level': level,
                'unfoldable': data['unfoldable'],
            })
        return lines
