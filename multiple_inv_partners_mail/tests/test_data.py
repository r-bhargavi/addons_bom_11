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


class PartnerMail(TransactionCase):
  
    def test_multiple_invoice_partner_mail(self):
        partner_a_id = self.env['res.partner'].create({
            'name': 'Partner A',
            'company_id': 1,
            'customer': True,
            'company_type': 'person',
        })
        partner_b_id = self.env['res.partner'].create({
            'name': 'Partner B',
            'company_id': 1,
            'customer': True,
            'company_type': 'person',
        })
        partner_c_id = self.env['res.partner'].create({
            'name': 'Partner C',
            'company_id': 1,
            'customer': True,
            'company_type': 'person',
        })
        parent_partner = self.env['res.partner'].create({
            'name': 'First Test',
            'company_id': 1,
            'customer': True,
            'company_type': 'person',
            'type':'invoice',
            'child_ids':[(6,0,[partner_a_id.id,partner_b_id.id,partner_c_id.id])]
        })
        partner_details = []
        if parent_partner.child_ids:
            for each in parent_partner.child_ids:
                # if len(each) > 1:
                if each.parent_id.type == 'invoice':
                    partner_details.append({
                        'child_name': each.name,
                        'parent_name': each.parent_id.name
                    })
                template_id = self.env.ref(
                        'multiple_inv_partners_mail.template_detected_multiple_inv_partners_child')
                print ("\n\n Test Runnig--------")
                return template_id.with_context(details=partner_details).send_mail(parent_partner.id)