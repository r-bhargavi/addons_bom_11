# -*- coding: utf-8 -*-
from odoo import http

# class SaleLineFilter(http.Controller):
#     @http.route('/sale_line_filter/sale_line_filter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_line_filter/sale_line_filter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_line_filter.listing', {
#             'root': '/sale_line_filter/sale_line_filter',
#             'objects': http.request.env['sale_line_filter.sale_line_filter'].search([]),
#         })

#     @http.route('/sale_line_filter/sale_line_filter/objects/<model("sale_line_filter.sale_line_filter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_line_filter.object', {
#             'object': obj
#         })