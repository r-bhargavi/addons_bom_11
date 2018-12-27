# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from datetime import datetime, time, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)

class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.model
    def create(self,values):
        return super(StockInventoryLine, self.with_context(inventory_line_creation = True)).create(values)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(StockInventoryLine, self).search(args, offset=offset, limit=limit, order=order, count=count)

        if res and res[0].inventory_id.is_to_be_merged and self.env.context.get("inventory_line_creation", False) : 
        #We force a false search result in case we're looking to forbid to have the same product in two different inventories
            # dom_keys = set(leaf[0] for leaf in dom)
            # merge_dom_keys = {'product_id', 'inventory_id.state', 'location_id', 'partner_id', 'package_id', 'prod_lot_id'}
            # if not (merge_dom_keys ^ dom_keys) : #if symetric difference is null
            args += [('inventory_id.state', '=', 'cancel')]
            return super(StockInventoryLine, self).search(args, offset=offset, limit=limit, order=order, count=count)
        return res

class StockInventory(models.Model):
    _inherit = "stock.inventory"

    is_to_be_merged = fields.Boolean("Is to be merged")

    def action_merge(self) :
        if len(self) < 2 :
            raise UserError(_("You should choose multiple inventories to merge"))
        if len(self.mapped("location_id")) != 1 :
            raise UserError(_("You cannot merge inventories with different locations")) 
        if not all((x.state == "confirm" and x.is_to_be_merged) for x in self) :
            raise UserError(_("You cannot merge inventories that are not in state progress or not marked as to be merged"))
        base_inventory = False
        for inventory in self :
            if not base_inventory :
                base_inventory = inventory
            else :
                for line in inventory.line_ids :
                    original_line = base_inventory.line_ids.filtered(lambda x : x.product_id.id == line.product_id.id)
                    if original_line :
                        original_line.product_qty += line.product_qty
                        line.unlink()
                    else : #assign line to base inventory
                        line.inventory_id = base_inventory.id
        for inventory in self.browse(self.ids) : #refresh
            if inventory.id != base_inventory.id :
                inventory.name += ' (merge part)'
                inventory.action_cancel_inventory()
            else :
                inventory.is_to_be_merged = False
                inventory.name += ' (merged result)'

#
#class stock_pack_operation(osv.osv):
#    _inherit = "stock.pack.operation"
#
#    def on_change_tests(self, cr, uid, ids, product_id, product_uom_id, product_qty, context=None):
#        res = super(stock_pack_operation, self).on_change_tests(cr, uid, ids, product_id, product_uom_id, product_qty, context)
#        if product_qty > 1000000 and 'warning' not in res:
#            product = self.pool.get('product.product').browse(cr, uid, [product_id], context=context)[0]
#            res['warning'] = {
#                        'title': _('Warning: wrong quantity!'),
#                        'message': _('The chosen quantity for product %s is way too much. It is probably a mistake.') % (product.name)
#                    }
#        return res

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def clean_empty_pickings(self) :
        _logger.debug("SEARCHING PICKINGS")
#        ('pack_operation_product_ids', '=', False), ('move_lines_related', '=', False)
        pickings = self.search([('state', '=', 'assigned'),('move_lines', '=', False)])
        for picking in pickings :
            _logger.debug(picking)
            picking.unlink()
            self.env.cr.commit()




        # product_obj = self.env.get('product.product')
        # inventory_obj = self.env.get('stock.inventory')
        # inventory = inventory_obj.browse(values.get("inventory_id"))
        # #Allow multiple inventories of same location with same products if the inventory is to be merged
        # if not inventory.is_to_be_merged : 
        #     dom = [('product_id', '=', values.get('product_id')), ('inventory_id.state', '=', 'confirm'),
        #            ('location_id', '=', values.get('location_id')), ('partner_id', '=', values.get('partner_id')),
        #            ('package_id', '=', values.get('package_id')), ('prod_lot_id', '=', values.get('prod_lot_id'))]
        #     res = self.search(dom)
        #     if res:
        #         location = self.env['stock.location'].browse(values.get('location_id'))
        #         product = product_obj.browse(values.get('product_id'))
        #         raise UserError(_("You cannot have two inventory adjustements in state 'in Progess' with the same product(%s), same location(%s), same package, same owner and same lot. Please first validate the first inventory adjustement with this product before creating another one.") % (product.name, location.name))
        # if 'product_id' in values and not 'product_uom_id' in values:
        #     values['product_uom_id'] = product_obj.browse(values.get('product_id')).uom_id.id
        # return super(StockInventoryLine, self).create(values) ##PROBLEM : super call with raise the UserError...

