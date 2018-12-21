from odoo import models, fields, api,_
from datetime import date


class PickingTemplateWizard(models.TransientModel):
    _name='picking.template.wizard'

    pickin_temp_ids=fields.Many2many('stock.picking.template', string='Picking Templates')


    # to assign product to selected picking template from wizard
    @api.multi
    def assign_product(self):
        product_id=self._context.get('active_id')
        for temp in self.pickin_temp_ids:
            # filter templates on wizard which are selected to assign product
            if temp:
                # to check whether product already exist on picking template line
                for tmp in temp:
                    exist_temp_line_id=self.env['stock.picking.template'].search([('temp_lines.product_id.id','=', product_id),('id','=',tmp.id)])
                    if not exist_temp_line_id:
                        vals={
                            'pick_temp_id':tmp.id,
                            'product_id':product_id,
                            'suggested_qty':0.0
                        }
                        temp_line_id=self.env['stock.picking.template.line'].create(vals)

# class PickingTemplate(models.TransientModel):
#     _name='picking.template'

#     name=fields.Char(string='Picking Template')
#     picking_type=fields.Many2one('stock.picking.type', string='Picking Type')
#     pick_date=fields.Date(string='Picking Date')
#     wizard_id = fields.Many2one('picking.template.wizard')
#     pick_temp_id=fields.Many2one('stock.picking.template')
#     assign=fields.Boolean(string='Assign to Product')
#     week_day=fields.Char(string='Day of Week')
#     categ=fields.Char(string='Category')