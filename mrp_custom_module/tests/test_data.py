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


class MrpCustomModule(TransactionCase):
  
    def test_mrp_custom_module(self):
        #to create mo for product template
        route_id = self.env['stock.location.route'].search([('name','=','Manufacture')], limit=1)
        product_a = self.env['product.template'].create({
            'name':'Product A',
            'type':'product',
            'route_ids':[(6, 0, [route_id.id])]
        })
        bom_id = self.env['mrp.bom'].create({
            'product_tmpl_id':product_a.id,
            'product_qty':1
        })
        product_product_a = self.env['product.product'].create({
            'name':'Product A',
            'product_tmpl_id':product_a.id
        })
        if bom_id:
            vals = {'product_id': product_product_a.id,
                    'product_qty': 1,
                    'bom_id': bom_id.id,
                    'product_uom_id': product_a.uom_id.id
                    }
            mo_id = self.env['mrp.production'].create(vals)
            if mo_id:
                mo_id.action_assign()
                mrp_product_produce_id = self.env['mrp.product.produce'].with_context({'active_id': mo_id.id}).create({
                    'mode':'consume_produce',
                    'product_qty':1
                })
                mrp_product_produce_id.do_produce()
                template = self.env.ref('mrp_custom_module.email_template_manufacturing_order', False)
            template.send_mail(mo_id.id, force_send=True)

        #to duplicate product template fully
        copy_product =  self.env['product.template'].create({
            'name':product_a.name,
            'type':product_a.type,
            'route_ids':product_a.route_ids.ids,
            'default_code':product_a.default_code if product_a.default_code else ''
        })
        bom_ids = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_a.id)])
        if bom_ids:
            default = None
            for each_bom in bom_ids:
                default_bom = dict(default or {})
                default_bom.setdefault('product_tmpl_id', copy_product.id)
                new_bom = each_bom.copy(default_bom)
            self.assertEqual(new_bom.product_tmpl_id.id, copy_product.id)
        print ("\n Test Runnig Sucessfully")



