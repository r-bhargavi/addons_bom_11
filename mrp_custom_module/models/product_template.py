# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _

from odoo.exceptions import UserError


class AddProduct(models.Model):
	_inherit = "product.template"
	
	product_variant_ids= fields.One2many('product.product', 'product_tmpl_id', 'Products', required=True,copy=True)
	attribute_line_ids=fields.One2many('product.attribute.line', 'product_tmpl_id', 'Product Attributes',copy=True)
	
	def write(self, vals):
		if self :
			temp_brw=self.browse(self.id)
			active=temp_brw.active
			if 'uom_id' in vals:
				new_uom = self.env['product.uom'].browse(vals['uom_id'])
				new_uom_categ=new_uom.category_id.id
				for product in self.browse(self.id):
					old_uom = product.uom_id
					old_uom_categ = product.uom_id.category_id.id
					# print "old_uomold_uom",old_uom,new_uom
					if old_uom != new_uom and old_uom_categ!=new_uom_categ:
						if active==False:
							# print "product.product_variant_idsproduct.product_variant_ids",product.product_variant_ids
							moves=self.env['stock.move'].search([('product_id.product_tmpl_id', '=', temp_brw.id), ('state', '=', 'done')], limit=1)
							if moves:
								raise UserError(_("Please try to duplicate product if you want to change UoM!!"))
		return super(AddProduct, self).write(vals)



# to duplicate product template fully
	@api.multi
	def copy_prod_template(self,default=None):
		default = dict(default or {})
		default.setdefault('type', 'product')
		# default.setdefault('week_number', self.week_number)
		default.setdefault('default_code', self.default_code if self.default_code else '')    
		bom_ids=self.env['mrp.bom'].search([('product_tmpl_id','=',self.id)])
		# res=super(AddProduct, self).copy(default=default)
		res = self.create({
			'name' :self.name,
			'type':'product',
			'default_code':self.default_code if self.default_code else ''
			})
		# res = self.copy(default)
		# print "new prodiuct-------------",res
		if bom_ids:
			default=None
			for each_bom in bom_ids:
				default_bom = dict(default or {})
				default_bom.setdefault('product_tmpl_id', res.id)
				new_bom=each_bom.copy(default_bom)
		return {
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'view_type': 'form',
				'res_model': 'product.template',
				'res_id': res.id,
				 }
	

						
# to open wizard with variants on product template form
	@api.multi
	def variants(self):
		view_ref = self.env['ir.model.data'].get_object_reference('mrp_custom_module', 'view_variants_product')
		view_id = view_ref[1] if view_ref else False
		return {
			# 'name': _('Message'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id,
			'res_model': 'add.product.wizard',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context':{'default_product_template':self.id, 'default_product_id' : self.product_variant_ids[0].id},
			}
