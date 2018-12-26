# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError,Warning
from odoo.tools.translate import _
from odoo import _, api, exceptions, fields, models
import odoo.addons.decimal_precision as dp
from datetime import datetime, time, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)

class MrpBomCostWizard(models.TransientModel):
    _name = "bom_cost_qty.wizard.mrp_bom_cost"
    _description = "Mrp Bom Cost Wizard"
    
    # to check if qty is edited through any of the source
    @api.multi
    @api.depends('component_ids','qty')
    def _check_edit_qty(self):
        for wiz in self :
            check_comp_edit_qty=[x.one_comp_qty_edited for x in wiz.component_ids]
            if wiz.qty==0.0 and True not in check_comp_edit_qty:
                wiz.qty_edited = False
            else:
                wiz.qty_edited = True

     # to raise a warning if qty is edited through one of the source
    @api.onchange("edit_qty_src")
    def onchange_edit_qty(self):
        for rec in self:
            if rec.qty_edited==True:
                raise UserError(_("Qty for one of the Source is already Edited!"))

    # to fetch all component lines of BoM on wizard
    @api.model
    def default_get(self, default_fields):
        res=super(MrpBomCostWizard,self).default_get(default_fields)
        active_id = self._context.get('active_id')
        bom_obj = self.env['mrp.bom']
        if active_id:
            bom_brw=bom_obj.browse(active_id)
            bom_lines = bom_brw.bom_line_ids
            res['component_ids'] = [
            (0, 0, {'orig_product_qty':x.product_qty,
            'edited_product_qty':x.product_qty,
            'product_uom':x.product_id.uom_id.id,
            'product_id':x.product_id.id,
            }) for x in bom_lines]
        return res

    # reset all values if more than 1 component line qty is edited
    @api.multi
    def print_report(self):
        comp_lines = self.component_ids.filtered( lambda line: line.one_comp_qty_edited==True)
        if len(comp_lines)>1:
            for each_comp in comp_lines:
                each_comp.write({'edited_product_qty':each_comp.orig_product_qty,'one_comp_qty_edited':False})
            self.write({'message':'Resetting all values to default as only material qty could be edited!!','qty_edited':False})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'bom_cost_qty.wizard.mrp_bom_cost',
                'target': 'new',
                'res_id': self.id,
                 }
        else:
            self.write({'qty_edited':True,'message':''})
            # return self.env['report'].get_action(self, 'mrp_bom_cost', data={'qty' : self.qty,
            #                    'ids' : self.bom.ids})
            record = self.env['mrp.bom'].browse(self._context.get('active_id'))
            return self.env.ref('mrp.action_report_bom_price').report_action(record)

    bom = fields.Many2one('mrp.bom', string='Bom', required=True, default=lambda self : self.env.context.get('active_id', False))
    qty = fields.Float('Quantity of finished product')
    component_ids = fields.One2many('wizard.component.lines','mrp_cost_id','Components')
    message = fields.Char(readonly=True,
        help='Message display when more then one raw material qty edited')    
    qty_edited = fields.Boolean('Qty Edited?',compute='_check_edit_qty',store=True)
    edit_qty_src = fields.Selection([('cmp_edit', 'Component Qty Edit'),
                                 ('fg_editl', 'Finished Good Qty Edit'),],
                                'Edit Qty Source', default='fg_editl',
                                help="To select whose qty needs to be edited either FG/Comp?")




class MrpBomCost(models.AbstractModel):
    _name = 'report.mrp_bom_cost'

    @api.multi
    def get_lines(self, boms, qty,components):
        product_lines = []
        check_comp_edited=[x.one_comp_qty_edited for x in components] 
        for bom in boms:
            ratio = qty and qty / bom.product_qty or 1
            products = bom.product_id
            if not products:
                products = bom.product_tmpl_id.product_variant_ids
            for product in products:
                attributes = []
                for value in product.attribute_value_ids:
                    attributes += [(value.attribute_id.name, value.name)]
                result, result2 = self.env['mrp.bom']._bom_explode(bom, product, 1)
                # to get qty on report if components are edited
                if True in check_comp_edited:
                    result=[]
                    edited_line_id=components.filtered(lambda line: line.one_comp_qty_edited==True)
                    ratio=(edited_line_id.edited_product_qty*bom.product_qty)/edited_line_id.orig_product_qty
                    qty=(edited_line_id.edited_product_qty*bom.product_qty)/edited_line_id.orig_product_qty
                    for each in components:
                        if each.one_comp_qty_edited==True:
                            final_qty=edited_line_id.edited_product_qty/ratio
                        else:
                            final_qty=each.orig_product_qty
                        line_data={'product_id':each.product_id.id,'product_qty':final_qty,'product_uom':each.product_uom.id}
                        result.append(line_data)
                product_line = {'product' : product, 'name': product.name, 'lines': [], 'total': 0.0,
                                'currency': self.env.user.company_id.currency_id,
                                'product_uom_qty': round(qty or bom.product_qty,2),
                                'product_uom': bom.product_uom,
                                'attributes': attributes}
                total = 0.0
                for bom_line in result:
                    line_product = self.env['product.product'].browse(bom_line['product_id'])
                    price_uom = self.env['product.uom']._compute_qty(line_product.uom_id.id, line_product.standard_price, bom_line['product_uom'])
                    line = {
                        'product_id': line_product,
                        'product_uom_qty': round(bom_line['product_qty'] * ratio,2),
                        'product_uom': self.env['product.uom'].browse(bom_line['product_uom']),
                        'price_unit': price_uom,
                        'total_price': price_uom * bom_line['product_qty'] * ratio,
                    }
                    total += line['total_price']
                    product_line['lines'] += [line]
                product_line['total'] = total
                product_lines += [product_line]
        return product_lines

    # @api.multi
    # def render_html(self, data=None):
    #     boms = self.env['mrp.bom'].browse(data and data.get("ids", False) or self.ids)
    #     wiz_id=data and data['context'].get('active_ids',False)
    #     wiz_brw=self.env['bom_cost_qty.wizard.mrp_bom_cost'].browse(wiz_id[0])
    #     res = self.get_lines(boms, wiz_brw.qty,wiz_brw.component_ids)
    #     return self.env['report'].render('mrp.mrp_bom_cost', {'lines': res})
    
    
class WizardComponentLines(models.TransientModel):
    _name = "wizard.component.lines"
    _description = "Mrp Cost Component Lines"
    
    product_id=fields.Many2one('product.product', 'Product', required=True, readonly=True)
    orig_product_qty= fields.Float('Original Product Quantity',required=True)
    edited_product_qty= fields.Float('Edited Product Quantity', required=True)
    product_uom= fields.Many2one('product.uom', 'Product Unit of Measure', required=True, readonly=True)
    mrp_cost_id=fields.Many2one('bom_cost_qty.wizard.mrp_bom_cost', 'MRP Cost Wizard', readonly=True)
    one_comp_qty_edited = fields.Boolean('Comp Qty edited?')

    # to check whether component qty is changed or not
    @api.onchange("edited_product_qty")
    def onchange_edit_qty(self):
        for rec in self:
            rec.one_comp_qty_edited=True
            if rec.edited_product_qty== rec.orig_product_qty:
                rec.one_comp_qty_edited=False
    
    
