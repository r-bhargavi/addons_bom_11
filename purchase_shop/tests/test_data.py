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
from datetime import datetime
from odoo import SUPERUSER_ID

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PurchaseShop(TransactionCase):
  
    def test_purchase_shop(self):
        #preload purchase line
        product_a = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'categ_id': 1,
        })
        product_b = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'categ_id': 1,
        })
        partner_id = self.env['res.partner'].create({
            'name':'Test Partner',
            'supplier':True,
        })
        po_vals = {
            'partner_id': partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': product_a.name,
                    'product_id': product_a.id,
                    'product_qty': 5.0,
                    'product_uom': product_a.uom_id.id,
                    'price_unit': 500.0,
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
                (0, 0, {
                    'name': product_b.name,
                    'product_id': product_b.id,
                    'product_qty': 5.0,
                    'product_uom': product_b.uom_id.id,
                    'price_unit': 250.0,
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })],
        }
        po_id = self.env['purchase.order'].create(po_vals)
        products = self.env['product.product'].search([('id','in',[product_a.id,product_b.id])])
        for product in products :
            product_lang = product.with_context({
                            'lang': partner_id.lang,
                            'partner_id': partner_id.id,
                            })
            # seller_info = product_lang.seller_ids.filtered(lambda x: x.name.id == partner_id.id and (not x.product_id or x.product_id.id == product_lang.id))
            # print ("\n\n seller info ==========>",seller_info)
            values = {
                'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'price_unit': 0.0,
                'product_qty': 0.0,
                'product_uom': product.uom_id.id,
                'name': product_lang.name,
                'order_id': po_id.id,
                'product_id': product.id,
            }
            if product_lang.description_purchase:
                values['name'] += '\n' + product_lang.description_purchase
            fpos =po_id.fiscal_position_id
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                values['taxes_id'] = fpos.map_tax(
                    product.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
            else:
                values['taxes_id'] = fpos.map_tax(product.supplier_taxes_id)
            line = self.env['purchase.order.line'].create(values)
            self.assertEquals(po_id.id,line.order_id.id)

        #action_remove_empty_lines
        for order in po_id:
            if order.state == 'draft' :
                order.order_line.filtered(lambda x : x.product_qty == 0).unlink()

        print ("\n\n Test Running--------")

