# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderServiceLine(models.Model) :
    _name = "sale.order.service.line"

    order_id = fields.Many2one('sale.order', 'Source Sale Order', ondelete='cascade', required=True)
    employee_id = fields.Many2one('hr.employee', 'Waiter', ondelete='cascade', required=True)
    confirmed = fields.Boolean("Confirmed")
    phone = fields.Char(related='employee_id.address_id.phone', string='Phone')
    email = fields.Char(related='employee_id.address_id.email', string='Email')
    comment = fields.Char(string='Comment')
        
class ChecklistLine(models.Model) :
    _name = "checklist.line"

    order_id_cl = fields.Many2one('sale.order', 'Source Sale Order', ondelete='cascade', required=True)
    confirmed = fields.Boolean("Confirmed")
    description = fields.Text(string='What?')
    who = fields.Text(string='Who?')
    when = fields.Date(string='When?')
#
#
class SaleOrder(models.Model) :
    _inherit = 'sale.order'

    service_lines = fields.One2many('sale.order.service.line', 'order_id', "Waiters")
    checklist_lines = fields.One2many('checklist.line', 'order_id_cl', "Check-list")