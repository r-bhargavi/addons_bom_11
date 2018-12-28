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


class MailStock(TransactionCase):
  
    def test_mail_out_of_stock(self):
        location_id = self.env['stock.location'].search([('name','=','Stock')], limit=1)
        location__dest_id = self.env['stock.location'].search([('name','=','Production')], limit=1)
        picking_type_id = self.env['stock.picking.type'].search([('name','=','Delivery Orders')],limit=1)
        partner_id = self.env["res.partner"].create({
            "name": "Test partner",
            "supplier": True,
            "is_company": True,
        })
        product_tmpl_id = self.env['product.template'].create({
            'name': 'Test Product',
            'type': 'product',
            'categ_id': 1
        })
        product_id = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'categ_id': 1,
            'product_tmpl_id': product_tmpl_id.id
        })
        stock_picking = self.env['stock.picking'].create({
            'location_id': location_id.id,
            'location_dest_id': location__dest_id.id,
            'partner_id': partner_id.id,
            'picking_type_id': picking_type_id.id,
        })
        stock_move = self.env['stock.move'].create({
            'name': 'move out',
            'location_id': location_id.id,
            'location_dest_id': location__dest_id.id,
            'product_id': product_id.id,
            'product_uom': product_id.uom_id.id,
            'product_uom_qty': 80.0,
            'procure_method': 'make_to_order',
            'picking_id': stock_picking.id,
        })
        final_list=[]
        for each_move in stock_move:
            # print ("\n\n each --------",each,each_move.product_id,each_move.location_dest_id)
            vals={}
            already_done = []
            if (each_move.product_id.id,each_move.location_dest_id) not in already_done :
                already_done.append((each_move.product_id.id,each_move.location_dest_id))
                available_qty = each_move.product_id.with_context({'location' : each_move.location_dest_id.id}).qty_available
                pid=each_move.product_id
                location_id=each_move.location_dest_id
                qty_avbl=available_qty
                # if qty_avbl < each_move.procurement_id.orderpoint_id.product_min_qty :
                vals={
                'product' : pid,
                'pid':pid.name,
                'location_id':location_id.display_name,
                'avbl_qty':qty_avbl,
                # 'orderpoint' : each_move.procurement_id.orderpoint_id,
                    }
                final_list.append(vals)
                create_vals = {
                    'product' : pid.id,
                    'location_id' : location_id.id,
                    'available_qty_uom' : qty_avbl,
                    'uom' : pid.uom_id.id,
                    # 'orderpoint' : each_move.procurement_id.orderpoint_id.id,
                    # 'procurement' : each_move.procurement_id.id,
                    }
                # if pid.uom_id :
                #     create_vals.update({
                #         'available_qty_shop_uom' : self.env['product.uom']._compute_quantity(pid.uom_id.id, qty_avbl, to_uom_id=pid.uom_id.id),
                #         'shop_uom' : pid.uom_id.id,
                #             })
                if len(final_list) > 0:
                    # template_id = self.env.ref('mail_out_of_stock.new_email_template_stock')
                        print ("\n Test Running-------")