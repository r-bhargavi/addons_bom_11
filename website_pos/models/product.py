# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit='product.product'

    # field to disable variant on pos
    unavailable_in_pos=fields.Boolean(string='Unavailable in the Point of Sale')
    # field to exclude variant from website
    exclude_from_website=fields.Boolean(string='Exclude From Website')