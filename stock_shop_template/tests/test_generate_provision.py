# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.addons.stock_shop_template.tests.test_data import TestData

from odoo import fields
from datetime import date, datetime, timedelta

import logging
_logger = logging.getLogger(__name__)
import odoo
import odoo.tests
import calendar

@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)


class TestPickingCase(TestData):
    def test_cron_generate_provision(self):
        
        day_today = date.today().weekday()
        week_day=calendar.day_name[day_today]
        _logger.debug(week_day)
        day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        day_names_eng =['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day = day_names[day_today]

        self.env['stock.location'].browse(self.supplier_location).write({'company_id':self.new_company.id})
#-----------------------Creating a picking templates with Product A and B Test1--------------------


        picking_template1=self.r_model_template.create({
        'week_days':'Sunday',
        'src_location':self.stock_location,
        'picking_type':self.picking_type_int.id,
        'dest_location':self.supplier_location,
        'temp_category':'Temp Categ1',
        })
        picking_template2=self.r_model_template.create({
        'week_days':'Monday',
        'src_location':self.stock_location,
        'picking_type':self.picking_type_int.id,
        'dest_location':self.supplier_location,
        'temp_category':'Temp Categ2',
        })
        print "self.stock_locationself.stock_location",self.stock_location
        chk_tmp_1_origin='['+str(picking_template1.dest_location.location_id.name)+']'+'['+day_names[day_names_eng.index(picking_template1.week_days)]+']'+'['+str(picking_template1.temp_category)+']',
        print "chk_tmp_1_originchk_tmp_1_origin",chk_tmp_1_origin[0]
        chk_tmp_2_origin='['+str(picking_template2.dest_location.location_id.name)+']'+'['+day_names[day_names_eng.index(picking_template2.week_days)]+']'+'['+str(picking_template2.temp_category)+']',
        print "chk_tmp_2_originchk_tmp_2_origin",chk_tmp_2_origin[0]
        picking_template3=self.r_model_template.create({
        'week_days':'Tuesday',
        'src_location':self.stock_location,
        'picking_type':self.picking_type_int.id,
        'dest_location':self.supplier_location,
        'temp_category':'Temp Categ3',
        })
#             creating template line 1 in above template
        tmp_line_1=self.env["stock.picking.template.line"].create({
            'product_id': self.productA.id,
            'pick_temp_id': picking_template1.id,
            'product_uom_id': self.productA.uom_id.id,
            'suggested_qty': 5,
            })
        tmp_line_2=self.env["stock.picking.template.line"].create({
            'product_id': self.productB.id,
            'pick_temp_id': picking_template2.id,
            'product_uom_id': self.productB.uom_id.id,
            'suggested_qty': 6,
            })
        tmp_line_3=self.env["stock.picking.template.line"].create({
            'product_id': self.productC.id,
            'pick_temp_id': picking_template3.id,
            'product_uom_id': self.productC.uom_id.id,
            'suggested_qty': 7,
            })
            
        result=self.r_model_template._cron_generate_provision()
        print "resultresultresultresult",result
        cron_generated_picks=self.r_model_picking.search([],order='id desc',limit=2)
        print "cron_generated_pickscron_generated_picks",cron_generated_picks
        for each in cron_generated_picks:
            for each_move in each.move_lines:
                if each_move.product_id.name=='test product1':
                    self.assertEquals(each_move.product_uom_qty, 5)
                elif each_move.product_id.name=='test product2':
                    self.assertEquals(each_move.product_uom_qty, 6)
            if 'Temp Categ2' in each.origin:
                self.assertEquals(each.origin, chk_tmp_2_origin[0])
            else:
                self.assertEquals(each.origin, chk_tmp_1_origin[0])
        #1) test picking generation
        # create 3 pickings template : one with the day today, one with next day, one with day after next day
        # call generate_provision
        # check that two pickings were created, with the day today and the day with the next day
        # check origin field is correctly computed
        # check that the pickings have the same product than template, with correct quantity
        # get products with week number in the templates to check if it's ignored/added correctly--this point m not clear
        
        
        
        
