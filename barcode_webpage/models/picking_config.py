# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ReataurantPickingConfig(models.Model):
    '''This model is for configuartion of restaurant internal picking's picking type, source location
        and destination location '''
    _name = 'restaurant.picking.config'

    name = fields.Char('Restaurant Name', required=1)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', required=1)
    source_location_id = fields.Many2one('stock.location', 'Source Location', required=1)
    destination_location_id = fields.Many2one('stock.location', 'Destination Location', required=1)
    barcode_nomenclature_id = fields.Many2one('barcode.nomenclature', string='Barcode Nomenclature', required=1)

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        if self.picking_type_id:
            self.source_location_id = self.picking_type_id.default_location_src_id
            self.destination_location_id = self.picking_type_id.default_location_dest_id

class StockPicking(models.Model):
    '''
    Inherit picking class to add boolean for restaurant internal transfer
    '''
    _inherit = 'stock.picking'

    is_restaurant_transfer = fields.Boolean('Restaurant Transfer', help='This will be true when internal picking '
                                                                        'created from barcode scaning')
    restaurant_conf_id = fields.Many2one('restaurant.picking.config', string='Restaurant')

    @api.model
    def process_restaurant_picking(self):
        '''
        Scheduler method that check draft restaurant picking and validate it
        :return: validate draft picking
        '''
        picking_env = self.env['stock.picking']
        picking_ids = picking_env.search([('is_restaurant_transfer', '=', True), ('state', '=', 'draft')])
        for picking_id in picking_ids:
            if picking_id.move_lines:
                picking_id.action_confirm()
                picking_id.action_assign()
                for pack in picking_id.pack_operation_ids:
                    if pack.product_qty > 0:
                        pack.write({'qty_done': pack.product_qty})
                    else:
                        pack.unlink()
                picking_id.do_transfer()




