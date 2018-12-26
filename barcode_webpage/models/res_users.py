from openerp import api, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    restaurant_config_ids = fields.Many2many('restaurant.picking.config', 'user_restaurantg_rel','user_id',
                                             'restaurant_id', string='Restaurant Picking')
    @api.model
    def scanProductBarcode(self, restaurant_id, barcode):
        error, message, lastProduct = False, False, False
        if restaurant_id and barcode :
            product = self.env['product.product']
            restaurant_env = self.env['restaurant.picking.config']
            restaurant =  restaurant_env.browse([int(restaurant_id)])
            result=restaurant.barcode_nomenclature_id.parse_barcode(barcode)
            product_id = product.search([('barcode','=',result.get('base_code'))], limit=1)
            if product_id:
                picking_env=self.env['stock.picking']
                stock_move_env = self.env['stock.move']
                picking = picking_env.search([('is_restaurant_transfer','=',True),('state', '=', 'draft'),('restaurant_conf_id','=',restaurant.id)])
                if picking:
                        stock_move_env.create({
                            'name':product_id.name,
                            'product_id':product_id.id,
                            'location_id': restaurant.source_location_id.id,
                            'location_dest_id': restaurant.destination_location_id.id,
                            'product_uom': product_id.uom_id.id,
                            'product_uom_qty': result['value'] and result['value'] or 1.0,
                            'picking_id': picking.id
                        })
                        message = 'Move created Successfully.'
                        lastProduct = product_id.name
                else:
                    picking.create({
                        'location_id': restaurant.source_location_id.id,
                        'location_dest_id': restaurant.destination_location_id.id,
                        'picking_type_id': restaurant.picking_type_id.id,
                        'restaurant_conf_id': restaurant.id,
                        'is_restaurant_transfer': True,
                        'move_lines':[(0,0,{
                            'name': product_id.name,
                            'product_id':product_id.id,
                            'product_uom': product_id.uom_id.id,
                            'product_uom_qty': result['value'] and result['value'] or 1.0,

                        })]
                    })
                    message = 'Picking created Successfully.'
                    lastProduct = product_id.name
            else:
                error = 'No Product Found!'
            return {'error':error, 'message':message, 'lastProduct': lastProduct}