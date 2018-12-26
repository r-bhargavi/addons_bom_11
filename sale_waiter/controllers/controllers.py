# -*- coding: utf-8 -*-
from odoo import http

# class SaleService(http.Controller):
#     @http.route('/sale_service/sale_service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_service/sale_service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_service.listing', {
#             'root': '/sale_service/sale_service',
#             'objects': http.request.env['sale_service.sale_service'].search([]),
#         })

#     @http.route('/sale_service/sale_service/objects/<model("sale_service.sale_service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_service.object', {
#             'object': obj
#         })