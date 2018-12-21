from odoo import models, fields, api,_
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api, exceptions
import calendar
import re

import logging
from odoo import SUPERUSER_ID


_logger = logging.getLogger(__name__)

class AddMissingProducts(models.Model):
    _name='add.missing.products'
    _rec_name='name'
    
    name=fields.Char(string='Name',required=True, copy=False)
    
#    to check all inventory belongs to same location
    @api.model
    def _dirty_check(self):
        ids = self._context.get('active_ids')
        if ids:
            if len(ids) >= 2:
                invt_ids = self.env['stock.inventory'].browse(ids)
                for d in invt_ids:
                    if d.location_id.id != invt_ids[0].location_id.id:
                        raise exceptions.Warning(
                            _('Not all inventory belongs to same location!'))
        return {}
    

        # to check all locations of stock inventory selected are same
    @api.model
    def default_get(self, default_fields):
        res=super(AddMissingProducts,self).default_get(default_fields)
        active_ids = self._context.get('active_ids')
        res.update({'name':'Add Missing Inventory'})
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AddMissingProducts, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=False)
        # print "res-------------------",res
        self._dirty_check()
        return res
    
    @api.multi
    def add_missing_products(self):
        orderpoint_obj=self.env['stock.warehouse.orderpoint']
        inventory_obj=self.env['stock.inventory']
        inv_prod=[]
        active_ids = self._context.get('active_ids')
        inventory_brw=inventory_obj.browse(active_ids)
        location_id= inventory_brw[0].location_id
        for each_invt in inventory_brw:
            if each_invt.product_id:
                inv_prod.append(each_invt.product_id.id)
            elif each_invt.line_ids:
                for each_line in each_invt.line_ids:
                    inv_prod.append(each_line.product_id.id)
        order_point_ids=orderpoint_obj.search([('location_id','=',location_id.id),('product_id','not in',inv_prod),('active','=',True)])
        if order_point_ids:
            # print "order_point_idsorder_point_ids",order_point_ids
            order_point_products=[]
            for each in order_point_ids:
                if each.product_id.active==True:
                    vals={
                    'product_id':each.product_id.id,
                    'product_uom_id':each.product_uom.id,
                    'location_id':location_id.id,
                    'product_qty':0.0
                    }
                    order_point_products.append((0,0,vals))
            inventory_id=inventory_obj.create({
            'name':'INVENTORY CREATION MISSING PRODUCTS'+' '+location_id.name,
            'location_id':location_id.id,
            })
            inventory_id.action_start()
            inventory_id.write({'line_ids':order_point_products})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.inventory',
                'target': 'new',
                'res_id': inventory_id.id,
                 }