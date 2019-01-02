# -*- coding: utf-8 -*-

# from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta
import pytz
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class sale_warning(TransactionCase):
  
    def test_sale_warning_cases(self):

        # sale_id= self.search([('team_id', '!=', 2), ('state', '=','sent'),('partner_id.email', '!=', False), '|', ('future_date','<=',current_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('future_date','=',False),
        #     ('requested_date','>',(current_date + relativedelta(days=+6)).strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        # create sale_order for test
        partner_id = self.env["res.partner"].create({
            "name": "Test partner",
            "supplier": True,
            "is_company": True,
        })
        sale_order_id = self.env['sale.order'].create({
            'name':'SO1221',
            'partner_id':partner_id.id
            })
        # added static id in code module for mail tempalte if not get then not execute
        if sale_order_id:
            #TODO : create template with external id
            template_id = 95
            mail_template = self.env['mail.template'].browse(template_id)
            for sale in sale_order_id:
                print ("\n\n mail tempalte-----",mail_template)
                # mail_template.send_mail(sale.id)

        # sent email every day
        current_date=date.today()
        sale_id= self.env['sale.order'].search([('team_id', '!=', 2), ('state', '=','sent'),('partner_id.email', '!=', False), '|', ('future_date','<=',current_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('future_date','=',False),
            ('requested_date','<=',(current_date + relativedelta(days=+6)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('requested_date','>',current_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        if sale_id:
            template_id = 96
            mail_template = self.env['mail.template'].browse(template_id)
            for sale in sale_id:
                print ("\n\n mail tempalte--------",mail_template)
                # mail_template.send_mail(sale.id)

        # remind confirm sale
        sale_id= self.env['sale.order'].search([('state', '=', 'sale'),('requested_date','>',current_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),('requested_date','<',(current_date + relativedelta(days=+2)).strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        if sale_id:
            for sale in sale_id:
                print ("\n\n salet --------",sale)
                # template = self.env.ref('sale_warning.email_template_confirm_sale')
                # template.send_mail(sale_id.id, force_send=True)
        print ("\n\n test case running sucessfully")