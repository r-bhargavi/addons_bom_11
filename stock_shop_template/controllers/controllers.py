# -*- coding: utf-8 -*-
from odoo import http

from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request

class StockShopTemplate(http.Controller):
    @http.route('/shop_orders', auth='user', website=True)
    def shop_orders(self,**kw):
        ensure_db()
        env=request.env
        rest_lst=[]
        if env.user and env.user.main_warehouse_id :
            user = env.user
            pickings_to_fill = env['stock.picking'].sudo().search([('picking_type_id.default_location_dest_id.location_id', '=', user.main_warehouse_id.lot_stock_id.location_id.id), ('temp_create_pick', '=', True), ('state', '=', 'draft')], order="scheduled_date asc, origin")
            return http.request.render('stock_shop_template.shop_orders',{'pickings':pickings_to_fill})
        

#     @http.route('/stock_shop_template/stock_shop_template/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_shop_template/stock_shop_template/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_shop_template.listing', {
#             'root': '/stock_shop_template/stock_shop_template',
#             'objects': http.request.env['stock_shop_template.stock_shop_template'].search([]),
#         })

#     @http.route('/stock_shop_template/stock_shop_template/objects/<model("stock_shop_template.stock_shop_template"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_shop_template.object', {
#             'object': obj
#         })