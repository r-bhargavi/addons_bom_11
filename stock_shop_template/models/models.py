# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from lxml import etree
from odoo import SUPERUSER_ID
from itertools import groupby
# class stock_shop_template(models.Model):
#     _name = 'stock_shop_template.stock_shop_template'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

import logging
from odoo import SUPERUSER_ID


_logger = logging.getLogger(__name__)

TEMPLATE_FLAG = "[template]"

class StockWarehouse(models.Model) :
	# _name = 'stock.picking'
	_inherit = 'stock.warehouse'

	user_ids = fields.One2many('res.users', 'main_warehouse_id', string='Users')


class StockMove(models.Model) :
    # _name = 'stock.picking'
    _inherit = 'stock.move'

    late = fields.Boolean('Late')

class StockWaitingScreenshot(models.Model):
    _name='stock.waiting.screenshot'


    shop=fields.Many2one('stock.location', string='Shop')
    product_id=fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Qty')
    uom_id=fields.Many2one('product.uom', string='Uom')
    date = fields.Date('Date')


class StockPicking(models.Model) :
    # _name = 'stock.picking'
    _inherit = 'stock.picking'
    
    #check login user main warehouse  user or not 
    @api.multi
    def check_login_user_main_wh_compute(self):
        main_wh = self.env.ref('stock.warehouse0', raise_if_not_found=False)
        login_user_wh=self.env.user.main_warehouse_id
        if login_user_wh!=main_wh and self.temp_create_pick==True:
            self.check_login_user_wh=True
        
    #check picking created from Template Cron
    temp_create_pick = fields.Boolean('Template Created Picking', readonly=1)
    check_login_user_wh = fields.Boolean('Main Wh User or Not',compute='check_login_user_main_wh_compute', store=False, help="If login user main warehouse  user boolean will be false")
    merged_picking = fields.Boolean('Merged picking', readonly=1)
    merged = fields.Boolean('Merged', readonly=1)

    # def action_done(self):
    #     res=super(StockPicking, self).action_done()
    #     if not self.merged_picking :
    #         picking = self.search([('id', '!=', self.id), ('merged_picking', '=', True), ('state', 'in',('confirmed','partially_available','assigned')), ('picking_type_id.id', '=', self.picking_type_id.id)])
    #         #if a merged picking has at least one move with one of the product moved here, copy it and deduct the quantities
    #         #TODO : do it in a cron to not slow down picking validation --> in merging picking !
    #         for pack_op in self.pack_operation_product_ids : #deduct from merged picking (it's easier to create a new picking than manipulate huge merged picking, very slow)
    #             move = self.env('stock.move').search([('picking_id.id', '!=', self.id),('picking_id.merged_picking', '=', True), ('picking_id.picking_type_id.id', '=', self.picking_type_id.id), 
    #                 ('picking_id.location_dest_id.id', '=', self.location_dest_id.id), ('picking_id.location_id.id', '=', self.location_id.id), 
    #                 ('product_id.id', '=', pack_op.product_id.id), ('picking_id.state', 'in',('confirmed','partially_available','assigned'))])
    #             move = move and move[0]

    
    # To set main company on click of  Mark as Todo button
    def action_confirm(self):
        res = super(StockPicking, self).action_confirm()
        company_changed = False
        for picking in self:
            mainwh=picking.env.ref('stock.warehouse0', raise_if_not_found=False)
            if picking.temp_create_pick==True and mainwh:
                if picking.company_id.id != mainwh.company_id.id :
                    company_changed = True
                    picking.company_id=mainwh.company_id.id

                for move_line in picking.move_lines:
                    move_line.company_id=mainwh.company_id.id
                    # to convert product_uom and quantity
                    move_line.product_uom_qty = picking.env['product.uom']._compute_qty(move_line.product_uom.id,
                                                                                     move_line.product_uom_qty,
                                                                                     move_line.product_id.uom_id.id)
                    move_line.product_uom = move_line.product_id.uom_id
                picking.env.ref('stock_shop_template.email_shop_order').send_mail(picking.id)
        return res


    def action_get_last_qties(self) :
        for picking in self:
            if self.state == 'draft' and self.origin:
                last_picking = self.search([('origin', '=', picking.origin), ('state', '=', 'done')])
                if last_picking :
                    for move in last_picking[0].move_lines :
                        new_move = picking.move_lines.filtered(lambda x : x.product_id.id == move.product_id.id)
                        if new_move :
                            new_move.write({'product_uom_qty' : move.product_uom_qty})
        return True


    # scheduler to merge pickings which belongs to same picking type, source and destination location, with picking type in picking template
    @api.model
    def merge_pickings(self) :
        pickings,filter_pickings,product_line=[],[],[]
        data_dict,vals={},{}
        array_index=0
        day_today = date.today().weekday()
        day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        day_names_eng =['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        self.env.cr.execute("select s.id from stock_picking as s where s.state in ('confirmed','partially_available','assigned') and (s.picking_type_id in (select t.picking_type from stock_picking_template as t))")
        pickin_ids=map(lambda x:x[0], self.env.cr.fetchall())
        # print "pickin_idspickin_ids",pickin_ids
        self.env.cr.execute("select distinct on ( picking_type_id, location_id, location_dest_id) id, picking_type_id, location_id, location_dest_id from stock_picking where id in %s ", (tuple(pickin_ids),))
        group_pickin_ids = map(lambda x: x[0], self.env.cr.fetchall())
        # print "group_pickin_idsgroup_pickin_ids",group_pickin_ids
        _logger.debug(group_pickin_ids)
        picking_ids=self.env['stock.picking'].browse(group_pickin_ids) #one picking by group
        pickin_ids=self.env['stock.picking'].browse(pickin_ids) #every picking concerned
        pickings_to_unlink = []
        for picking in picking_ids:
            _logger.debug(picking.picking_type_id.name)
            pickings.append(picking)
        for pick in pickings:
            filtered_picking_ids=pickin_ids.filtered(lambda l:l.location_id==pick.location_id and l.location_dest_id==pick.location_dest_id) #gather the pickings from the group
            if filtered_picking_ids:
                # for filter_pick in filtered_picking_ids:
                #     pickings.remove(filter_pick)
                filter_pickings.append(filtered_picking_ids)
        for filter_picking in filter_pickings:
            for pickin in filter_picking[0]:
                _logger.debug(pickin.picking_type_id.name)
                _logger.debug(len(filter_picking))
#                create new picking vals
                vals={
                        'location_id':pickin.location_id.id,
                        'location_dest_id':pickin.location_dest_id.id,
                        'picking_type_id':pickin.picking_type_id.id,
                        'merged_picking' : True,
                    }
            merged_picking_id= self.env['stock.picking'].create(vals)
            # print "merged_picking_idmerged_picking_id",merged_picking_id
            _logger.debug(merged_picking_id)
            #TODO : check if qties were sent during the day and remove them from the main picking
            data_dict = {}
            data_late = {}
            data_becoming_late = {}
            for pickin in filter_picking:
                # print "filtter pickings-------"
                for pick_product in pickin.move_lines:
                    if pick_product.product_uom_qty and (pick_product.late or pick_product.becoming_late) :
                        _logger.debug("sould have been send today or before, maybe substracted later")
                        _logger.debug(pick_product.product_id.name)
                        _logger.debug("keep it separately")
                        if pick_product.product_id.id in data_late :
                            data_late[pick_product.product_id.id].product_uom_qty += pick_product.product_uom_qty
                        else :
                            pick_product.write({'picking_id':merged_picking_id.id, 'late' : True, 'becoming_late' : False})
                            data_late[pick_product.product_id.id]=pick_product

                    elif pick_product.product_uom_qty and pickin.merged_picking and pick_product.product_id.x_order_days and day_names[day_today] in pick_product.product_id.x_order_days : #and day_names[(day_today - 1) % 7] in pick_product.product_id.x_order_days :
                       #merged means that it was ordered before today, and today was a production day, so it should be sent tomorrow
                        _logger.debug("should be send tomorrow")
                        _logger.debug(pick_product.product_id.name)
                        _logger.debug("keep it separately")
                        if pick_product.product_id.id in data_becoming_late :
                            data_becoming_late[pick_product.product_id.id].product_uom_qty += pick_product.product_uom_qty
                        else :
                            pick_product.write({'picking_id':merged_picking_id.id, 'becoming_late' : True})
                            data_becoming_late[pick_product.product_id.id]=pick_product
                        
                    elif pick_product.product_id.id not in data_dict and pick_product.product_uom_qty:
#                        update new picking id in move 
                        pick_product.write({'picking_id':merged_picking_id.id})
                        data_dict[pick_product.product_id.id]=pick_product
                    elif pick_product.product_id.id in data_dict : #merge if same product

                        data_dict[pick_product.product_id.id].product_uom_qty += pick_product.product_uom_qty
                    # if not ordered today, and production day was yesterday but not today, it should have been seen today, so if it is present, it is late
                    
                pickin.merged = True
                pickin.action_cancel()
                if pickin.temp_create_pick and not self.env['stock.move'].search([('picking_id', '=', pickin.id)]) :
                    pickings_to_unlink.append(pickin) #remove because if no moves, picking will remain in draft mode
            base_picking = filter_picking[0]
            _logger.debug(date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            _logger.debug(base_picking.picking_type_id.name)
            _logger.debug(self.search([('picking_type_id', '=', base_picking.picking_type_id.id), ('state', '=', 'done'), 
                ('scheduled_date', '>=', date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT) ), ('scheduled_date', '<=', (date.today() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT) )]))
            #substract qties sent today
            for picking_done in self.search([('picking_type_id', '=', base_picking.picking_type_id.id), ('state', '=', 'done'), 
                ('scheduled_date', '>=', date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT) ), ('scheduled_date', '<=', (date.today() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT) )]) :
                _logger.debug(picking_done)
                _logger.debug(data_dict)
                _logger.debug(data_late)
                for pack_op in picking_done.pack_operation_product_ids :
                    _logger.debug(pack_op.product_id.name)
                    _logger.debug(pack_op.product_id.id)
                    if (pack_op.product_id.id in data_dict) or (pack_op.product_id.id in data_late) :
                        rounded_qty = pack_op.qty_done
                        _logger.debug(rounded_qty)
                        if pack_op.product_id.picking_uom_id :
                            #convert in picking_uom 
                            rounded_qty = pack_op.env['product.uom']._compute_qty(pack_op.product_uom_id.id,
                                                                                     pack_op.qty_done,
                                                                                     pack_op.product_id.picking_uom_id.id, rounding_method="HALF-UP")
                            #reconvert un product_uom to get rounded value
                            _logger.debug(rounded_qty)
                            rounded_qty = pack_op.env['product.uom']._compute_qty(pack_op.product_id.picking_uom_id.id,
                                                                                     rounded_qty,
                                                                                     pack_op.product_uom_id.id, rounding_method="HALF-UP")
                            _logger.debug(rounded_qty)
                        if pack_op.product_id.id in data_late :
                            #substract first the late quties
                            _logger.debug("substract from late")
                            new_rounded_qty = max(rounded_qty - data_late[pack_op.product_id.id].product_uom_qty, 0)
                            data_late[pack_op.product_id.id].product_uom_qty = max(data_late[pack_op.product_id.id].product_uom_qty - rounded_qty,0)
                            rounded_qty = new_rounded_qty
                            _logger.debug(rounded_qty)
                        if rounded_qty and pack_op.product_id.id in data_becoming_late :
                            _logger.debug("substract from becoming late")
                            new_rounded_qty = max(rounded_qty - data_becoming_late[pack_op.product_id.id].product_uom_qty, 0)
                            data_becoming_late[pack_op.product_id.id].product_uom_qty = max(data_becoming_late[pack_op.product_id.id].product_uom_qty - rounded_qty,0)
                            rounded_qty = new_rounded_qty
                            _logger.debug(rounded_qty)
                        if rounded_qty and pack_op.product_id.id in data_dict :
                            #still qties to remove from not late moves
                            _logger.debug("substract from not late")
                            data_dict[pack_op.product_id.id].product_uom_qty = max(data_dict[pack_op.product_id.id].product_uom_qty - rounded_qty,0)
            if merged_picking_id:
                merged_picking_id.action_confirm()
                merged_picking_id.force_assign() #set it ready to scan
                merged_picking_id.do_prepare_partial() #reset operations

                screenshot = self.env['stock.waiting.screenshot']
                for move in merged_picking_id.move_lines :
                    if move.product_uom_qty == 0 :
                        move.late = False
                        move.becoming_late = False
                    else :
                        screenshot.create({
                            'product_id' : move.product_id.id,
                            'shop' : move.location_dest_id.id,
                            'qty' : move.product_uom_qty,
                            'uom_id' : move.product_uom.id,
                            'date' : date.today(),
     
                            })
        for picking in pickings_to_unlink :
            picking.unlink()

