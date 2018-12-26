# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request

class BarcodePage(http.Controller):
    '''This controller define to access barcode web page and based on scanned product it create  picking'''

    @http.route('/page/barcode', auth='user', website=True)
    def barcode(self,**kw):
        ensure_db()
        env=request.env
        rest_lst=[]
        if env.user and env.user.restaurant_config_ids:
            for restaurant in env.user.restaurant_config_ids:
                rest_lst.append(restaurant)
            #return http.request.render('barcode_webpage.restaurant_home',{'restaurant':rest_lst})
            return http.local_redirect('/web#action=scanbarcode.ui')
        else:
            return http.request.render('barcode_webpage.no_access_restaurant_url')

    # code is commented because functionality move to js function
    # @http.route('/scan', type='http', auth="user", methods=['POST'], csrf=False)
    # def create_picking(self, **post):
    #     '''This method call after scanning barcode it check scanned product and create picking for that product'''
    #     error = False
    #     message = False
    #     lastProduct = False
    #     env = request.env
    #     if env.user and env.user.restaurant_config_ids:
    #         rest_lst = []
    #         for restaurant in env.user.restaurant_config_ids:
    #             rest_lst.append(restaurant)
    #     if post.get('restaurant') and post.get('product_barcode') :
    #         barcode = post.get('product_barcode')
    #         product = env['product.product']
    #         restaurant_env = env['restaurant.picking.config']
    #         restaurant =  restaurant_env.browse([int(post.get('restaurant'))])
    #         rest_lst.remove(restaurant)
    #         rest_lst.insert(0, restaurant)
    #         result=restaurant.barcode_nomenclature_id.parse_barcode(barcode)
    #         product_id = product.search([('barcode','=',result.get('base_code'))], limit=1)
    #         if product_id:
    #             picking_env=env['stock.picking']
    #             stock_move_env = env['stock.move']
    #             picking = picking_env.search([('is_restaurant_transfer','=',True),('state', '=', 'draft'),('restaurant_conf_id','=',restaurant.id)])
    #             if picking:
    #                 stock_move_env.create({
    #                     'name':product_id.name,
    #                     'product_id':product_id.id,
    #                     'location_id': restaurant.source_location_id.id,
    #                     'location_dest_id': restaurant.destination_location_id.id,
    #                     'product_uom': product_id.uom_id.id,
    #                     'product_uom_qty': result['value'] and result['value'] or 1.0,
    #                     'picking_id': picking.id
    #                 })
    #                 message = 'Move created Successfully.'
    #                 lastProduct = product_id.name
    #             else:
    #                 picking.create({
    #                     'location_id': restaurant.source_location_id.id,
    #                     'location_dest_id': restaurant.destination_location_id.id,
    #                     'picking_type_id': restaurant.picking_type_id.id,
    #                     'restaurant_conf_id': restaurant.id,
    #                     'is_restaurant_transfer': True,
    #                     'move_lines':[(0,0,{
    #                         'name': product_id.name,
    #                         'product_id':product_id.id,
    #                         'product_uom': product_id.uom_id.id,
    #                         'product_uom_qty': result['value'] and result['value'] or 1.0,

    #                     })]
    #                 })
    #                 message = 'Picking created Successfully.'
    #                 lastProduct = product_id.name
    #         else:
    #             error = 'No Product Found!'
    #         return request.render('barcode_webpage.restaurant_home',{'restaurant':rest_lst, 'default':restaurant, 'error':error, 'message':message, 'lastProduct':lastProduct})

    #     else:
    #         return http.request.render('barcode_webpage.no_access_restaurant_url')

