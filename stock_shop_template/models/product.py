
from openerp import models, fields, api,_


class ProductProduct(models.Model):
    _inherit='product.product'

    template_line_ids=fields.One2many('stock.picking.template.line','product_id',string='Template Lines')
    picking_uom_id = fields.Many2one('product.uom', string='Picking Unit of Measure')

    # to select picking template
    @api.multi
    def select_pick_template(self):
        # picking_temp_lines=[]
        ctx={}
        # picking_temp_ids=self.env['stock.picking.template'].search([('temp_lines.product_id.id','!=', self.id)])
        # for temp in picking_temp_ids:
        #     temp_lines=(0,0,{
        #         'name':temp.name,
        #         'picking_type':temp.picking_type.id,
        #         'pick_date':temp.temp_date,
        #         'pick_temp_id':temp.id,
        #         'categ':temp.temp_category,
        #         'week_day':temp.week_days
        #     })
        #     picking_temp_lines.append(temp_lines)
        # ctx={'default_pickin_temp_ids':picking_temp_lines}
        compose_form_id=self.env.ref('stock_shop_template.assign_picking_temp_wizard_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'picking.template.wizard',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def _check_uom(self, context=None):
        for product in self.browse(cursor, user, ids, context=context):
            if product.picking_uom_id and (product.uom_id.category_id.id != product.picking_uom_id.category_id.id) :
                return False
        return True

    _constraints = [
        (_check_uom, 'Error: The default Unit of Measure and the Picking Unit of Measure must be in the same category.',['uom_id', 'picking_uom_id']),
    ]

class ProductTemplate(models.Model):
    _inherit='product.template'

    week_number = fields.Selection([
        (1, 'Week 1'),
        (2, 'Week 2'),
        (3, 'Week 3'),
        (4, 'Week 4')
    ], string='Number of the week to publication')
