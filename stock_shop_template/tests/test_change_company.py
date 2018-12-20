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


class TestCompanyChange(TestData):

    def test_change_company(self):


#----------------------------------Testing Compnay Change Test3-------------------------------------

        picking_template1=self.r_model_template.create({
        'week_days':'Sunday',
        'src_location':self.stock_location,
        'picking_type':self.picking_type_int.id,
        'dest_location':self.supplier_location,
        'temp_category':'Temp Categ',
        })
#             creating template line 1 in above template
        tmp_line_1=self.env["stock.picking.template.line"].create({
            'product_id': self.productA.id,
            'pick_temp_id': picking_template1.id,
            'product_uom_id': self.productA.uom_id.id,
            'suggested_qty': 5,
            })
        
        picking_template1.write({'company_id':self.new_company.id})
        template_lines=[]
        for line in picking_template1.temp_lines:
            tmp_lines={
                'product_id':line.product_id.id,
                'name': line.product_id.partner_ref,
                'product_uom_qty':line.suggested_qty,
                'product_uom': line.product_id.uom_id.id,
                'location_id':
                    picking_template1.src_location.id or
                    self.env.ref('stock.stock_location_stock').id,
                'location_dest_id':
                    picking_template1.dest_location.id or
                    self.env.ref('stock.stock_location_customers').id,
            }
            template_lines.append((0,0,tmp_lines))

        vals={
                    'partner_id':picking_template1.partner_id.id,
                    'location_id':picking_template1.src_location.id,
                    'location_dest_id':picking_template1.dest_location.id,
                    'picking_type_id':picking_template1.picking_type.id,
                    'move_lines': (template_lines)
                }
        new_picking=self.r_model_picking.create(vals)
        self.assertNotEqual(new_picking.company_id.id, picking_template1.company_id.id, 'Companies are not same')
        new_picking.action_confirm()

#3) test company changes :
        # get a picking template from another company and generate the picking
        # assert that the picking is from the other company
        # mark the picking as to do
        # check that the picking is now from the main company
        
        
        