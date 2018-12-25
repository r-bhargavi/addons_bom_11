# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from odoo import SUPERUSER_ID


_logger = logging.getLogger(__name__)
# class sale_line_filter(models.Model):

class SaleOrder(models.Model) :
    _inherit = 'sale.order'
    _name = 'sale.order'

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault('message_follower_ids', False)
        default.setdefault('partner_id', 37921)    
        default.setdefault('partner_shipping_id', 37921)    
        default.setdefault('partner_invoice_id', 37921)    
        return super(SaleOrder, self).copy(default)

    to_invoice = fields.Boolean("To invoice (fix)", default=True)

    @api.model
    def check_to_invoice(self) :
        res = self.search([('state', 'in', ('sale', 'done')), ('to_invoice', '=', True), [u'date_order', u'>', u'2016-12-30 23:00:00'], ['partner_id.id', 'not in', [8709,19308,30779,6578, 33810, 24827, 16359, 6584,30778, 25173, 25867, 25868, 25174, 25171]]], limit=2000, order="date_order desc")
        _logger.debug("NB SO TO COMPUTE")
        _logger.debug(len(res))
        res.filtered(lambda x : x.invoice_ids).write({'to_invoice' : False})
            
            # if len(so.invoice_ids) :
            #     _logger.debug(so)
            #     so.to_invoice = False


class CrmLead(models.Model) :
    _inherit = 'crm.lead'
    _name = 'crm.lead'

    date_event = fields.Datetime("Date de l'événement")