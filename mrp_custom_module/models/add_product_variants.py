# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class AddProduct(models.TransientModel):
    _name = "add.product.wizard"

    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Float(string="Quantity", default=1.0)
    product_template = fields.Many2one('product.template', )

# to create mo for product template
    @api.multi
    def create_mo(self):
        produce_obj=self.env['mrp.product.produce']
        if self.product_id:
            bom_obj = self.env['mrp.bom'].search([('product_tmpl_id','=',self.product_template.id), '|', ('product_id' ,'=', False), ('product_id', '=', self.product_id.id)],limit=1)
            
                # to create mo if bom exists for product template of select product variant
            if bom_obj:
                vals={'product_id':self.product_id.id,'product_qty':self.qty,'bom_id':bom_obj.id,'product_uom_id':self.product_id.uom_id.id}
                mo_id=self.env['mrp.production'].create(vals)
                if mo_id:
                    # mo_id.action_compute()
                    mo_id.action_assign()
                    # mo_id.signal_workflow('button_confirm')
                    # mo_id.force_production()
                    # mo_id.signal_workflow('button_produce')
                    produce_id = produce_obj.with_context({'active_ids': [mo_id.id], 'active_id': mo_id.id}).create({
                       'mode': 'consume_produce',
                       'product_qty': self.qty})
                    # lines = produce_id.on_change_qty(mo_id.product_qty, [])
                    # produce_id.write(lines['value'])
                    produce_id.do_produce()

                        # To send mail after mo created
                template = self.env.ref('mrp_custom_module.email_template_manufacturing_order', False)
                if template:
                    if template.email_to:
                        template.send_mail(mo_id.id, force_send=True)
                    else:
                        raise UserError('email is not defined in the template')
            else:
                raise UserError('Bill of Material is not defined for the selected product')