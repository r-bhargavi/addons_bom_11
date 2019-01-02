# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from odoo.tests.common import SavepointCase
# from odoo.addons.pos_survey.tests.test_data import TestData
#
# from odoo import fields
# import logging
# _logger = logging.getLogger(__name__)
# import odoo
# import odoo.tests
# @odoo.tests.common.at_install(False)
# @odoo.tests.common.post_install(True)

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo.tests.common import TransactionCase


class ProcessPicking(TransactionCase):
  
    def test_process_restarunt(self):
        location_id = self.env['stock.location'].search([('name', '=', 'Stock')], limit=1)
        location__dest_id = self.env['stock.location'].search([('name', '=', 'Production')], limit=1)
        stock_picking_type = self.env['stock.picking.type'].search([('name','=','Delivery Orders')], limit=1)
        partner_id = self.env['res.partner'].create({
            'name':'Test Customer',
            'customer':True
        })
        product_a = self.env['product.product'].create({
            'name':'Product A',
            'type':'product',
        })
        product_b = self.env['product.product'].create({
            'name': 'Product B',
            'type': 'product',
        })
        move_line_a = self.env['stock.move'].create({
            'name': 'move out',
            'location_id': location_id.id,
            'location_dest_id': location__dest_id.id,
            'product_id': product_a.id,
            'product_uom': product_a.uom_id.id,
            'product_uom_qty': 10,
            'procure_method': 'make_to_order',
            'quantity_done': 10
        })
        move_line_b = self.env['stock.move'].create({
            'name': 'move out',
            'location_id': location_id.id,
            'location_dest_id': location__dest_id.id,
            'product_id': product_b.id,
            'product_uom': product_b.uom_id.id,
            'product_uom_qty': 10,
            'procure_method': 'make_to_order',
            'quantity_done': 10
        })
        stock_picking = self.env['stock.picking'].create({
            'location_id': location_id.id,
            'location_dest_id': location__dest_id.id,
            'partner_id': partner_id.id,
            'picking_type_id': stock_picking_type.id,
        })
        # stock_picking.write({
        #     'move_lines':[(6,0,[move_line_a.id,move_line_b.id])]
        # })

        for picking_id in stock_picking:
            if picking_id.move_lines:
                picking_id.action_confirm()
                picking_id.action_assign()
                for pack in picking_id.pack_operation_ids:
                    if pack.product_qty > 0:
                        pack.write({'qty_done': pack.product_qty})
                    else:
                        pack.unlink()
                picking_id.do_transfer()

        # scanProductBarcode

        barcode_nomec = self.env['barcode.nomenclature'].create({
            'name':'test barcode'
        })

        res_picking_config = self.env['restaurant.picking.config'].create({
            'name':'Restarunt',
            'picking_type_id':stock_picking_type.id,
            'source_location_id':location_id.id,
            'destination_location_id':location__dest_id.id,
            'barcode_nomenclature_id':barcode_nomec.id
        })
        error, message, lastProduct = False, False, False
        # restaurant = restaurant_env.browse([int(restaurant_id)])
        # result = restaurant.barcode_nomenclature_id.parse_barcode(barcode)
        # product_id = product.search([('barcode', '=', result.get('base_code'))], limit=1)
        
        if product_a:
            picking = self.env['stock.picking'].search([('is_restaurant_transfer', '=', True), ('state', '=', 'draft'),
                                          ('restaurant_conf_id', '=', res_picking_config.id)])
            if picking:
                self.env['stock.move'].create({
                    'name': product_a.name,
                    'product_id': product_a.id,
                    'location_id': res_picking_config.source_location_id.id,
                    'location_dest_id': res_picking_config.destination_location_id.id,
                    'product_uom': product_a.uom_id.id,
                    'product_uom_qty': 1,
                    'picking_id': picking.id
                })
                print ('Move created Successfully')
                lastProduct = product_a.name
            else:
                picking.create({
                    'location_id': res_picking_config.source_location_id.id,
                    'location_dest_id': res_picking_config.destination_location_id.id,
                    'picking_type_id': res_picking_config.picking_type_id.id,
                    'restaurant_conf_id': res_picking_config.id,
                    'is_restaurant_transfer': True,
                    'move_lines': [(0, 0, {
                        'name': product_a.name,
                        'product_id': product_a.id,
                        'product_uom': product_a.uom_id.id,
                        'product_uom_qty': 1.0,
                    })]
                })
            print ('Picking created Successfully')
            lastProduct = product_a.name
