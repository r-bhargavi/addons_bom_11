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


class Product_tags(TransactionCase):
  
    def test_write_product_tags(self):
        product_a = self.env['product.template'].create({
            'name':'Product A',
            'type':'product',
            'categ_id':1,
            'default_code':'EVENTS'
        })
        product_b = self.env['product.template'].create({
            'name': 'Product B',
            'type': 'product',
            'categ_id': 1,
            'default_code': 'EVENTS'
        })
        product_c = self.env['product.template'].create({
            'name': 'Product B',
            'type': 'product',
            'categ_id': 1,
            'default_code': 'ABELAG'
        })
        tag_a = self.env['crm.lead.tag'].create({
            'name':'Tag A'
        })
        tag_b = self.env['crm.lead.tag'].create({
            'name': 'Tag B'
        })
        tag_c = self.env['crm.lead.tag'].create({
            'name': 'Tag C'
        })
        products = self.env['product.template'].search([('default_code', 'ilike', 'EVENTS')])
        products.write({'tag_ids': [(6, 0, [tag_a.id, tag_b.id])]})
        products = self.env['product.template'].search([('default_code', 'ilike', 'ABELAG')])
        products.write({'tag_ids': [(6, 0, [tag_a.id, tag_c.id])]})

        #check invoice
        res = self.env['sale.order'].search([('state', 'in', ('sale', 'done')), ('to_invoice', '=', True),
                           [u'date_order', u'>', u'2016-12-30 23:00:00'], ['partner_id.id', 'not in',
                                                                           [8709, 19308, 30779, 6578, 33810, 24827,
                                                                            16359, 6584, 30778, 25173, 25867, 25868,
                                                                            25174, 25171]]], limit=2000,
                          order="date_order desc")
        res.filtered(lambda x: x.invoice_ids).write({'to_invoice': False})
        print ("\n\n Test Run Successfull---------")



