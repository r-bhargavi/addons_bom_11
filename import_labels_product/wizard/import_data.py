# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo.exceptions import ValidationError,UserError
import re
from xlrd import open_workbook
import base64
import datetime

class ImportData(models.TransientModel):
    _name = "import.data"

    file_name = fields.Char()
    load_file = fields.Binary('Load File', attachment=True)
    label_type = fields.Many2one('label.type',string="Label Type")

#to import product label excel file
    @api.multi
    def import_order_data(self):
        data_file = base64.b64decode(self.load_file)
        order_code_keys,array_index = {},0
        final_list=[]
        product_obj = self.env['product.product']
        wb = open_workbook(file_contents=data_file)
        sheet = wb.sheet_by_index(0)
        for row in range(1, sheet.nrows):
                product_french = sheet.cell(row, 0).value
                product_dutch = sheet.cell(row, 1).value
                ingredients = sheet.cell(row, 3).value
                poids_net = sheet.cell(row, 5).value
                unite = sheet.cell(row, 6).value
                kcal = sheet.cell(row, 7).value
                kj = sheet.cell(row, 8).value
                lip = sheet.cell(row, 9).value
                ags = sheet.cell(row, 10).value
                glu = sheet.cell(row, 11).value
                sucre = sheet.cell(row, 12).value
                prot = sheet.cell(row, 13).value
                sel = sheet.cell(row, 14).value
                dlc = sheet.cell(row, 15).value
                t_degree = sheet.cell(row, 16).value
                g_ml = sheet.cell(row, 17).value
                code_ean = sheet.cell(row, 18).value
                product=product_obj.search([('barcode','=',code_ean)],limit=1)
                if not product:
                    product=product_obj.search([('product_french','=',product_french)],limit=1)
                elif not product:
                    product=product_obj.search([('product_dutch','=',product_dutch)],limit=1)
                len_ingredients=len(ingredients.split(','))
                product_vals = {
                            'poids_net': poids_net,
                            'barcode': code_ean,
                            'label_type': self.label_type.id,
                            'kcal': kcal,
                            'kj': kj,
                            'lip': lip,
                            'ags': ags,
                            'glu': glu,
                            'sucre': sucre,
                            'prot': prot,
                            'sel': sel,
                            'dlc': dlc,
                            't_degree': t_degree,
                            'per_ml': g_ml,
        #                    'product_french': product_french,
        #                    'product_dutch': product_dutch,
        #                    'ingredients': ingredients,
                        }
               
                if product:
                    if len_ingredients>self.label_type.max_length:
                        raise UserError(_("Length of Ingredients for product (%s) is greater then max length defined for ingredients in label type selected which is (%s).") % (code_ean, self.label_type.max_length))
                    product.write(product_vals)
#                else:
#                    product_vals.update({'name':code_ean})
#                    product = product_obj.create(product_vals)
#                print "product create---------------",product
        return True