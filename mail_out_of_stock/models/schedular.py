# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockOutHistory(models.Model) :
    _name = 'stock.out.history'

    product = fields.Many2one('product.product', string='Product', required=True)
    location_id = fields.Many2one('stock.location', string='Emplacement', required=True)
    available_qty_uom = fields.Float('Quantity',required=True)
    uom = fields.Many2one('product.uom', string='Unit of Measure')
    available_qty_shop_uom = fields.Float('Quantity')
    shop_uom = fields.Many2one('product.uom', string='Unit of Measure')

    orderpoint = fields.Many2one('stock.warehouse.orderpoint', string='Orderpoint', required=True)
    procurement = fields.Many2one('procurement.order', string='Procurement', required=True)
    date = fields.Date(string='date', default=fields.Date.context_today, required=True)

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    # scheduler to send mail when procuremnt product running out of stock

    @api.model
    def automatic_send_mail_poutstck(self):
        out_of_stock=self.get_out_of_stock_products()
        if out_of_stock is not False:
            template_id = self.env.ref('mail_out_of_stock.new_email_template_stock')
            # email_to=template_id.email_id.ids
            # recipient_ids= [(4, pid) for pid in email_to]
            template_id.with_context(get_out_of_stock_products=out_of_stock).send_mail(543881)

    @api.model
    def get_out_of_stock_products(self):
        move_obj=self.env['stock.move']
        history=self.env['stock.out.history']
        # move_ids=move_obj.with_context(lang="fr_BE").search([('product_id.active','=',True),('procurement_id','!=',False),('procurement_id.orderpoint_id','!=',False), ('procurement_id.orderpoint_id.active','=',True),('procurement_id.state','in',('running','confirmed','cancel')), ('picking_type_id.code', '=', 'internal')])
        move_ids=move_obj.with_context(lang="fr_BE").search([('picking_type_id.code', '=', 'internal'),('group_id','!=',False),('product_id.active','=',True),('state','in',['confirmed','cancel'])])
        final_list=[]
        if move_ids:
            vals={}
            already_done = []
            for each_move in move_ids:
                if (each_move.product_id.id,each_move.location_dest_id) not in already_done :
                    already_done.append((each_move.product_id.id,each_move.location_dest_id))
                    available_qty = each_move.product_id.with_context({'location' : each_move.location_dest_id.id}).qty_available
                    pid=each_move.product_id
                    location_id=each_move.location_dest_id
                    qty_avbl=available_qty
                    # if qty_avbl < each_move.procurement_id.orderpoint_id.product_min_qty :
                    vals={
                    'product' : pid,
                    'pid':pid.name,
                    'location_id':location_id.display_name,
                    'avbl_qty':qty_avbl,
                    # 'orderpoint' : each_move.procurement_id.orderpoint_id,
                    } 
                    final_list.append(vals)
                    create_vals = {
                        'product' : pid.id,
                        'location_id' : location_id.id,
                        'available_qty_uom' : qty_avbl,
                        'uom' : pid.uom_id.id,
                        # 'orderpoint' : each_move.procurement_id.orderpoint_id.id,
                        # 'procurement' : each_move.procurement_id.id,
                        }
                    if pid.uom_id :
                        create_vals.update({
                                'available_qty_shop_uom' : self.env['product.uom']._compute_quantity(pid.uom_id.id, qty_avbl, to_uom_id=pid.uom_id.id),
                                'shop_uom' : pid.uom_id.id,
                                })
                    # history.create(create_vals)
        return final_list if len(final_list)>0 else False
         