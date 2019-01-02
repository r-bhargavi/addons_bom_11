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
_logger = logging.getLogger(__name__)


class MergeInventory(TransactionCase):
  
    def test_merge_stock_inventiry(self):
        
        # clean_empty_pickings
        # Note : this module is dependes in the "stock_barcode" and action_merge method is define in py but not calling from anyware so not add test case and module is not installable it depends on other
        pickings = self.search([('state', '=', 'assigned'),('move_lines', '=', False)])
        for picking in pickings :
            _logger.debug(picking)
            picking.unlink()