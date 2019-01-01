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
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class Sale_amendment(TransactionCase):
  
    def test_sale_amendment(self):
        partner_id = self.env['res.partner'].create({
            'name': 'Test Partner',
            'supplier': True,
            'customer':True
        })
        product_a = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'categ_id': 1,
        })
        so_id = self.env['sale.order'].create({
            'partner_id': partner_id.id,
            'partner_invoice_id': partner_id.id,
            'partner_shipping_id': partner_id.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'order_line': [
                (0, 0, {
                    'name': product_a.name,
                    'product_id': product_a.id,
                    'product_uom_qty': 2,
                    'price_unit': 500.0,
                })
                ],
        })
        so_id.action_confirm()
        # rais the error below code say sale.order has no attributes picking_ids but there is a picking_ids field check that
        # for pick in so_id.picking_ids:
        #     print("\n\n picking ids--------", pick)
        #     if pick.state == 'done':
        #         print ('Unable to amend this sales order. You must first cancel all receptions related to this sales order.')
        #         print ("\n\n if =======")
        #     else:
        #         print ("\n\n cancel----")
        #         pick.filtered(lambda r: r.state != 'cancel').action_cancel()

        company = self.env.ref('base.main_company')
        journal = self.env['account.journal'].create(
            {'name': 'Purchase Journal - Test', 'code': 'STPJ', 'type': 'purchase', 'company_id': company.id})
        account_payable = self.env['account.account'].create({'code': 'X1111', 'name': 'Sale - Test Payable Account',
                                                              'user_type_id': self.env.ref(
                                                                  'account.data_account_type_payable').id,
                                                              'reconcile': True})
        account_income = self.env['account.account'].create({'code': 'X1112', 'name': 'Sale - Test Account',
                                                             'user_type_id': self.env.ref(
                                                                 'account.data_account_type_direct_costs').id})
        invoice_vals = {
            'name': '',
            'type': 'in_invoice',
            'partner_id': partner_id.id,
            'invoice_line_ids': [(0, 0, {'name': product_a.name, 'product_id': product_a.id, 'quantity': 2,
                                         'uom_id': product_a.uom_id.id, 'price_unit': product_a.standard_price,
                                         'account_id': account_income.id})],
            'account_id': account_payable.id,
            'journal_id': journal.id,
            'currency_id': company.currency_id.id,
        }
        inv = self.env['account.invoice'].create(invoice_vals)
        so_id.invoice_ids = [(6, 0, [inv.id])]
        for inv in so_id.invoice_ids:
            if inv.state not in ('cancel', 'draft'):
                prin('Unable to amend this sales order. You must first cancel all Customer Invoices related to this sales order.')
            else:
                res = inv.filtered(lambda r: r.state != 'cancel').action_invoice_cancel()
                self.assertEquals(res,True)
            so_id.action_cancel()

            # create_amendment method flow
            for order in so_id:
                create_vals = {
                    'sale_amendment_id': order.id,
                    'name': order.name,
                    'amendment': order.revision + 1,
                    'amount_untaxed ': order.amount_untaxed,
                    'amount_tax': order.amount_tax,
                    'amount_total': order.amount_total,
                    'quotation_date': order.date_order,
                    'amendment_line': [],
                }
                line_data = []
                for line in so_id.order_line:
                    line_data.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'unit_price': line.price_unit,
                        'discount': line.discount,
                        'subtotal': line.price_subtotal,
                    }))
                create_vals['amendment_line'] = line_data
                sale_amendment_id = self.env['sale.amendment'].create(create_vals)
                self.assertEquals(sale_amendment_id.sale_amendment_id.id,so_id.id)
                print ("\n\n Test Running ----")



