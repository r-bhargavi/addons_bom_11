# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
import pytz
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit='sale.order'
    
    
    future_date = fields.Date(string='Start remind date', states={'draft': [('readonly', False)]}, required=False)
    
    def onchange_requested_date(self, cr, uid, ids, requested_date,
                                commitment_date, context=None):
        if requested_date:
            current_date=datetime.now().date()
            req_date = datetime.strptime(str(requested_date), '%Y-%m-%d %H:%M:%S')
            # to check that the requested date is not less than the current date
            if req_date.date()< current_date and uid != 8: #avoid accounting user
                warning = {
                    'title': (_('Warning!')),
                    'message': (_('Requested Date should not be less than current date!'))
                }
                return {'warning': warning}
                #for tomorrow and it's over 5 pm
            tz = pytz.timezone('Europe/Brussels')
            if req_date.date() == current_date + timedelta(days=1) and datetime.now(tz).hour > 17 :
                warning = {
                    'title': (_('Warning!')),
                    'message': (_("Un events pour demain alors qu'il est passé 17h !"))
                }
                return {'warning': warning}
        return super(SaleOrder, self).onchange_requested_date(cr, uid, ids, requested_date, commitment_date, context=context)



    @api.multi
    @api.constrains('x_jetable','x_return')
    def _check_return(self):
        for order in self:
            if order.x_jetable and not order.x_return :
                raise ValueError(_('Error: Plat blanc mais pas de date de retour.'))
        
    @api.model
    def cron_send_email_data_week(self):
        current_date=date.today()
        sale_id= self.search([('team_id', '!=', 2), ('state', '=','sent'),('partner_id.email', '!=', False), '|', ('future_date','<=',current_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('future_date','=',False),
            ('requested_date','>',(current_date + relativedelta(days=+6)).strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        if sale_id:
            #TODO : create template with external id
            template_id = 95
            mail_template = self.env['mail.template'].browse(template_id)
            for sale in sale_id:
                mail_template.send_mail(sale.id)
# #                convert string to datetime format
#                 requested_date=datetime.strptime(sale.requested_date,'%Y-%m-%d %H:%M:%S').date()
# #                Add 7 days domain
#                 due_date=requested_date+relativedelta(days=+6)
# #                check current date with due date
                # if due_date < current_date  :

                
               # sale.force_quotation_send()
                    
    @api.model
    def cron_send_email_data_everyday(self):
        current_date=date.today()
        sale_id= self.search([('team_id', '!=', 2), ('state', '=','sent'),('partner_id.email', '!=', False), '|', ('future_date','<=',current_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('future_date','=',False),
            ('requested_date','<=',(current_date + relativedelta(days=+6)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('requested_date','>',current_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        if sale_id:
            template_id = 96
            mail_template = self.env['mail.template'].browse(template_id)
            for sale in sale_id:
                mail_template.send_mail(sale.id)
# #                convert string to datetime format
#                 requested_date=datetime.strptime(sale.requested_date,'%Y-%m-%d %H:%M:%S').date()
# #                Add 7 days domain
#                 due_date=date.today()-relativedelta(days=+6)
# #                check current date with order date
#                 if requested_date <= current_date and requested_date >= due_date:
#                     sale.force_quotation_send()
    
    def notify_customer(self,sale_id):
        # Find the e-mail template
        template = self.env.ref('sale_warning.email_template_confirm_sale')
        ctx = dict()
        return template.send_mail(sale_id.id, force_send=True)
    
    @api.model
    def cron_remind_confirm_sale(self):
        current_date=date.today()
        sale_id= self.search([('state', '=', 'sale'),('requested_date','>',current_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),('requested_date','<',(current_date + relativedelta(days=+2)).strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        if sale_id:
            for sale in sale_id:
                self.notify_customer(sale)