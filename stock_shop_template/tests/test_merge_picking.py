# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase
from openerp.addons.stock_shop_template.tests.test_data import TestData

from openerp import fields
import logging
_logger = logging.getLogger(__name__)
import openerp
import openerp.tests
@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)


class TestPickingMerge(TestData):
  
    def test_merge_pickings(self):

#       ----------------- Creating an internal shipment for testing merge pickings Test2-------------------------------

            picking_template=self.r_model_template.create({
            'week_days':'Sunday',
            'src_location':self.stock_location,
            'picking_type':self.picking_type_int.id,
            'dest_location':self.supplier_location,
            'temp_category':'Temp Categ1',
            })
    #             creating template line 1 in above template
            tmp_line_1=self.env["stock.picking.template.line"].create({
                'product_id': self.productA.id,
                'pick_temp_id': picking_template.id,
                'product_uom_id': self.productA.uom_id.id,
                'suggested_qty': 5,
                })

            picking_int1 = self.r_model_picking.create({
                'partner_id': self.partner.id,
                'picking_type_id': self.picking_type_int.id,
                'location_id': self.stock_location,
                'location_dest_id':self.supplier_location })
            print "picking_int1picking_int1-----------------------------",picking_int1
            picking_int2 = self.r_model_picking.create({
                'partner_id': self.partner.id,
                'picking_type_id': self.picking_type_int.id,
                'location_id': self.stock_location,
                'location_dest_id':self.supplier_location })
            print "picking_int2picking_int2-----------------------------",picking_int2
    #        
    ##        I check that both the pickings created are in draft initially
            self.assertEquals(picking_int1.state, 'draft')
            self.assertEquals(picking_int2.state, 'draft')

    #        creating move 1 in internal shipemnt1
            move1=self.env["stock.move"].create({
                'name': self.productA.name,
                'product_id': self.productA.id,
                'product_uom_qty': 3,
                'product_uom': self.productA.uom_id.id,
                'picking_id': picking_int1.id,
                'location_id': self.stock_location,
                'location_dest_id': self.supplier_location})
    #            
    #            creating move2 in internal shipment1
            move2=self.env["stock.move"].create({
                'name': self.productB.name,
                'product_id': self.productB.id,
                'product_uom_qty': 3,
                'product_uom': self.productB.uom_id.id,
                'picking_id': picking_int1.id,
                'location_id': self.stock_location,
                'location_dest_id':self.supplier_location })

    #        creating move 3 in internal shipemnt2
            move3=self.env["stock.move"].create({
                'name': self.productC.name,
                'product_id': self.productC.id,
                'product_uom_qty': 3,
                'product_uom': self.productC.uom_id.id,
                'picking_id': picking_int2.id,
                'location_id': self.stock_location,
                'location_dest_id': self.supplier_location})
    #            
    #            creating move4 in internal shipment2
            move4=self.env["stock.move"].create({
                'name': self.productB.name,
                'product_id': self.productB.id,
                'product_uom_qty': 5,
                'product_uom': self.productB.uom_id.id,
                'picking_id': picking_int2.id,
                'location_id': self.stock_location,
                'location_dest_id':self.supplier_location })

    #            confirming internal shipemnt
            picking_int1.action_confirm()
            picking_int2.action_confirm()
    #        checking state of pickings post mark as to do
            print "state of shipment111111=----------",picking_int1.state
            print "state of shipment222222=----------",picking_int2.state

    ##        testing merge pickings functioanlaity
            self.r_model_picking.merge_pickings()
            
            merge_id=self.r_model_picking.search([],order='id desc',limit=1)
            print "merge_idmerge_idmerge_idmerge_id",merge_id
            self.assertEquals(len(merge_id.move_lines), 3)

            for each in merge_id.move_lines:
                if each.product_id.name=='test product1':
                    self.assertEquals(each.product_uom_qty, 3)
                elif each.product_id.name=='test product2':
                    self.assertEquals(each.product_uom_qty, 8)
                elif each.product_id.name=='test productC':
                    self.assertEquals(each.product_uom_qty, 3)
            
    #        state of original pickings post merge pickings
            self.assertEquals(picking_int2.state, 'cancel')
            
            
            #2) test picking merge :
        # create 2 pickings, one with product A and B and on other with product B and C.
        # mark them as todo
        # check their state
        # call merge picking
        # check that there are cancelled, and a new picking is present with products A,B and C and with quantities summed