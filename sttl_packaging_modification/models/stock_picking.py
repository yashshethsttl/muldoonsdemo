# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_packaging_create(self,move_lines_to_pack=False):
        """
        This method is used to create a new packaging record.
        """
        for move in self:
            move_line_ids = move._package_move_lines(move_lines_to_pack=move_lines_to_pack)
            if move_line_ids and move_line_ids.filtered(lambda x: x.product_packaging_id):
                res = move._pre_put_in_pack_hook(move_line_ids)
                if not res:
                    move.action_create_packaging()
                    # move.action_without_divided_create_packaging()
                    move.action_divided_create_packaging(move_line_ids)
                    return res
            raise UserError(_("There is nothing eligible to put in a pack. Either there are no quantities to put in a pack or all products are already in a pack."))
    
    def action_divided_create_packaging(self,move_line_ids):
        for move in self:
            for move_line in move.move_ids_without_package.filtered(lambda x: x.product_packaging_id and x.product_id.tracking == 'serial'):
                search_move = move_line_ids.search([('move_id','=',move_line.id)],order="result_package_id asc")
                if search_move:
                    move_line_ids_list = search_move.ids
                    chunks = []
                    n = search_move.mapped('product_packaging_id').qty
                    # Iterate and slice the list
                    for i in range(0, len(move_line_ids_list), int(n)):
                        chunks.append(move_line_ids_list[i:i + int(n)])
                    for chunk in chunks:
                        # Create a new packaging record for each chunk
                        move_ids = move.env['stock.move.line'].browse(chunk)
                        package = move._put_in_pack(move_ids)
                        move._post_put_in_pack_hook(package)
    
    def action_without_divided_create_packaging(self):
        for move in self:
            if move.move_ids_without_package.filtered(lambda x: not x.product_packaging_id):
                move_lines = move.move_ids_without_package.filtered(lambda x: not x.product_packaging_id)
                for move_line in move_lines:
                    package = move._put_in_pack(move_line.move_line_ids)
                    move._post_put_in_pack_hook(package)

    def action_create_packaging(self):
        for move in self:
            if move.move_ids_without_package.filtered(lambda x: x.product_packaging_id and x.product_id.tracking != 'serial'):
                move_lines = move.move_ids_without_package.filtered(lambda x: x.product_packaging_id and x.product_id.tracking != 'serial')
                for move_line in move_lines:
                    if move_line.picking_id:
                        move_line.picking_id.write({
                            'move_line_ids':[(3, move_line.move_line_ids.ids)]
                        })
                    move_line.write({
                        'move_line_ids': [(5, 0, 0)],
                    })
                    qty = int(move_line.product_packaging_id.qty)
                    move_line_product_uom_qty = move_line.product_uom_qty

                    result = []
                    remaining_qty = move_line_product_uom_qty

                    while remaining_qty > 0:
                        if remaining_qty >= qty:
                            result.append(qty)
                            remaining_qty -= qty
                        else:
                            result.append(remaining_qty)
                            remaining_qty = 0
                    for i in result:
                        create_move_line = self.env['stock.move.line'].create({
                            'product_id': move_line.product_id.id,
                            'quantity': i,
                            'location_id': move_line.location_id.id,
                            'location_dest_id': move_line.location_dest_id.id,
                            'picking_id': move_line.picking_id.id,
                            'move_id': move_line.id,
                        })
                        move_line.move_line_ids = [(4, create_move_line.id)]
                        package = move._put_in_pack(create_move_line)
                        move._post_put_in_pack_hook(package)
