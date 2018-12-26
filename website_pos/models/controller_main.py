# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSale(WebsiteSale):
    # to exclude product variants from publishing on website
    def get_attribute_value_ids(self, product):
        attrs=super(WebsiteSale, self).get_attribute_value_ids(product)
        if attrs:
            n=0
            for attr_id in attrs:
                product_id=request.env['product.product'].browse(attr_id[0])
                if product_id.exclude_from_website==True:
                    attrs.pop(n)
                n+=1
        return attrs