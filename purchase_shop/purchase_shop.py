# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from datetime import datetime, time, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging
from odoo import SUPERUSER_ID


_logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = 'res.users'
    main_warehouse_id = fields.Many2one('stock.warehouse', string='Main Warehouse', default=lambda self : self.env.ref('stock.warehouse0', raise_if_not_found=False))

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_default_warehouse(self):
        wh = self.env.ref('stock.warehouse0', raise_if_not_found=False)
        if wh:
            return wh.ids
        return []

    purchase_warehouse_ids = fields.Many2many('stock.warehouse', 'res_partner_stock_warehouse_default_rel',
        string='Who can purchase from this supplier', default=_get_default_warehouse)

class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    _inherit = 'purchase.order'

    @api.model
    def _default_picking_type_user(self):
        type_obj = self.env['stock.picking.type']
        #CUSTOM : default picking type = to user shop
        _logger.debug("DEFAULT PICKING TYPE !!!!!!!!!!!!")
        types = self.env.user.main_warehouse_id and type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', self.env.user.main_warehouse_id.id)])
        if not types:
            return self._default_picking_type()
        return types[:1]

    @api.model
    def _get_default_warehouse(self):
        return self.env.user.main_warehouse_id
        #return [self.env.user.pos_config.stock_location_id.warehouse_id.id]

    @api.depends('order_line.date_planned')
    def _compute_date_planned(self):
        for order in self:
            min_date = False
            for line in order.order_line:
                if not min_date or line.date_planned < min_date:
                    min_date = line.date_planned
            if min_date:
                order.date_planned = min_date
            else : 
                order.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    #UPDATE METHOD REF
    picking_type_id = fields.Many2one(default=_default_picking_type_user)
    purchase_warehouse_id = fields.Many2one('stock.warehouse',
        string='Purchased by', default=_get_default_warehouse)
    date_planned = fields.Datetime(compute='_compute_date_planned')

    @api.multi
    def action_preload_lines(self) :
        self.ensure_one()
        search_dom = [('purchase_ok', '=', True),('purchase_warehouse_variants', '=', self.purchase_warehouse_id.id), ('product_tmpl_id.seller_ids.name', '=', self.partner_id.id)]
        products = self.env['product.product'].search(search_dom)
        purchase_line_obj = self.env['purchase.order.line']
        _logger.debug('PRODUCTS')
        _logger.debug(products)
        _logger.debug(search_dom)
        for product in products :
            product_lang = product.with_context({
                            'lang': self.partner_id.lang,
                            'partner_id': self.partner_id.id,
                            })
            seller_info = product_lang.seller_ids.filtered(lambda x : x.name.id == self.partner_id.id and (not x.product_id or x.product_id.id == product_lang.id))
            if seller_info :
                seller_info = seller_info[0]

                values = {
                    'date_planned' : datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'price_unit' : 0.0,
                    'product_qty' : 0.0,
                    'product_uom' : product.uom_po_id.id or product.uom_id.id,
                    'name' : "[%s] %s" % (seller_info.product_code or product_lang.default_code, seller_info.product_name or product_lang.name),
                    'order_id' : self.id,
                    'product_id' : product.id,
                }
                if product_lang.description_purchase:
                    values['name'] += '\n' + product_lang.description_purchase

                fpos = self.fiscal_position_id
                if self.env.uid == SUPERUSER_ID:
                    company_id = self.env.user.company_id.id
                    values['taxes_id'] = fpos.map_tax(product.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
                else:
                    values['taxes_id'] = fpos.map_tax(product.supplier_taxes_id)


                line = purchase_line_obj.create(values)
            #line.onchange_product_id()

    @api.multi
    def action_remove_empty_lines(self) :
        for order in self:
            if order.state == 'draft' :
                order.order_line.filtered(lambda x : x.product_qty == 0).unlink()

class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'

    _inherit = 'purchase.order.line'


    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(PurchaseOrderLine, self).onchange_product_id()
        if not self.product_id:
            return result
        self.product_uom = not self.env.user.has_group('purchase.group_purchase_manager') and self.product_id.uom_po_secondary_id or self.product_id.uom_po_id or self.product_id.uom_id

        self._onchange_quantity()
        return result


# class ProductProduct(models.Model):
#     _inherit = 'product.product'

    # @api.multi
    # def is_purchasable(self):
    #     for product in self:
    #         _logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Can be purchased ? product product")
    #         product.can_be_purchased = product.product_tmpl_id.can_be_purchased


    # can_be_purchased = fields.Boolean()

# class PurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'

#     product_id = fields.Many2one('product.product',domain=[('purchase_ok', '=', True),('can_be_purchased', '=', True)])


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    # @api.multi
    # def is_purchasable(self):
    #     for product in self:
    #         _logger.debug("################################Can be purchased ?")
    #         _logger.debug(product.purchase_warehouse_ids)
    #         product.can_be_purchased = self.user_has_groups('purchase.group_purchase_manager') or (self.env.user.pos_config and \
    #             bool(product.purchase_warehouse_ids.filtered(lambda x : x.id == self.env.user.pos_config.stock_location_id.warehouse_id.id)))

    # @api.model
    # def _get_default_warehouse(self):
    #     return [6, 0, ref()]
        #return [self.env.user.pos_config.stock_location_id.warehouse_id.id]

    @api.model
    def _get_default_warehouse(self):
        wh = self.env.ref('stock.warehouse0', raise_if_not_found=False)
        _logger.debug('DEFAULT WAREHOUSE')
        _logger.debug(wh)
        if wh:
            return wh.ids
        return []

    uom_po_secondary_id = fields.Many2one('product.uom', string='Purchase Secondary Unit of Measure', help="Secondary Unit of Measure used for purchase orders. It must be in the same category than the default unit of measure.")
    purchase_warehouse_ids = fields.Many2many('stock.warehouse', 'product_template_stock_warehouse_default_rel',
        string='Can be purchased by', default=_get_default_warehouse)

    @api.multi
    @api.constrains('uom_id', 'uom_po_secondary_id')
    def _check_uom_sec(self):
        for product in self:
            if product.uom_po_secondary_id and product.uom_id.category_id.id != product.uom_po_secondary_id.category_id.id:
                raise ValueError(_('Error: The default Unit of Measure and the secondary purchase Unit of Measure must be in the same category.'))


    # can_be_purchased = fields.Boolean(compute=is_purchasable)
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.model
    def _get_default_warehouse(self):
        wh = self.env.ref('stock.warehouse0', raise_if_not_found=False)
        _logger.debug('DEFAULT WAREHOUSE')
        _logger.debug(wh)
        if wh:
            return wh.ids
        return []

    purchase_warehouse_variants = fields.Many2many('stock.warehouse', 'product_product_stock_warehouse_default_rel',
        string='Can be purchased by', default=_get_default_warehouse)