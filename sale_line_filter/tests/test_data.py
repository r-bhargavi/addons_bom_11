# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.addons.sale_line_filter.tests.test_data import TestData

from odoo import fields
import logging
_logger = logging.getLogger(__name__)
import odoo
import odoo.tests
@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)


class sale_line_filter(TestData):
  
    def sale_line_filter_product_tags(self):
        product_1 = self.env['product.template'].create({
            'name':'test product 1',
            'type':'product',
            'categ_id':1,
            'default_code':'EVENTS'
            })
        product_2 = self.env['product.template'].create({
            'name':'test product 2',
            'type':'product',
            'categ_id':1,
            'default_code':'EVENTS'
            })
        tag_1 = self.env['crm.lead.tag'].create({
            'name':'test tag 1'
            })
        tag_2 = self.env['crm.lead.tag'].create({
            'name':'test tag 2'
            })
        products = self.search([('default_code', 'ilike', 'EVENTS')])
        product.write({'tag_ids' : [(6,0,[tag_1.id,tag_2.id])]})
        products = self.search([('default_code', 'ilike', 'ABELAG')])
        product.write({'tag_ids' : [(6,0,[tag_1.id,tag_2.id])]})