# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # def button_validate(self):
    #     res = super(StockPicking, self).button_validate()
    #     for rec in self:
    #         moves = rec.move_ids_without_package.sorted('sequence')
    #         sections_to_remove = self.env['stock.move']

    #         for index, move in enumerate(moves):
    #             if move.display_type == 'line_section':
    #                 # Get the next move (if exists)
    #                 next_move = moves[index + 1] if index + 1 < len(moves) else None

    #                 # If next move is not a product line, mark section for deletion
    #                 if not next_move or next_move.display_type in ('line_section', 'line_note'):
    #                     sections_to_remove |= move

    #         if sections_to_remove:
    #             sections_to_remove.unlink()

    #     return res

    def button_validate(self):
        for rec in self:
            moves = rec.move_ids_without_package.sorted('sequence')
            sections_to_remove = self.env['stock.move']

            last_section = None
            for move in moves:
                if move.display_type == 'line_section':
                    last_section = move
                elif move.display_type not in ('line_section', 'line_note'):
                    if last_section:
                        move.parent_section_id = last_section.id

            res = super(StockPicking, self).button_validate()

            for backorder in rec.backorder_ids:
                new_moves = backorder.move_ids_without_package.sorted('sequence')

                for move in new_moves:
                    if move.display_type not in ('line_section', 'line_note'):
                        parent_section = move.parent_section_id
                        if parent_section and not parent_section.is_section_added_in_backorder:
                            parent_section.copy({
                                'picking_id': backorder.id,
                                'sequence': move.sequence - 1
                            })
                            parent_section.is_section_added_in_backorder = True

            refreshed_moves = rec.move_ids_without_package.sorted('sequence')
            for index, move in enumerate(refreshed_moves):
                if move.display_type == 'line_section':
                    next_move = refreshed_moves[index + 1] if index + 1 < len(refreshed_moves) else None
                    if not next_move or next_move.display_type in ('line_section', 'line_note'):
                        sections_to_remove |= move

            if sections_to_remove:
                sections_to_remove.unlink()
        return res

    def do_print_picking(self):
        picking_operations_report = self.env.ref('sttl_picking_section.action_report_picking_sn',raise_if_not_found=False)
        if not picking_operations_report:
            raise UserError(_("The Picking Operations report has been deleted so you cannot print at this time unless the report is restored."))
        self.write({'printed': True})
        return picking_operations_report.report_action(self)
