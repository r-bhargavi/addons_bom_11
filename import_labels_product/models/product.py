
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit='product.product'

    label_type = fields.Many2one('label.type', string='Label Type')
    poids_net=fields.Char(string='POIDS NET', copy=False)
    kcal=fields.Float(string='KCAL', copy=False)
    kj=fields.Float(string='KJ', copy=False)
    lip=fields.Float(string='LIP', copy=False)
    ags=fields.Float(string='AGS', copy=False)
    glu=fields.Float(string='GLU', copy=False)
    sucre=fields.Float(string='sucre', copy=False)
    prot=fields.Float(string='PROT', copy=False)
    sel=fields.Float(string='SEL', copy=False)
    dlc=fields.Float(string='DLC', copy=False)
    t_degree=fields.Char(string='T-DEGREE', copy=False)
    per_ml=fields.Char(string='100 g/ml', copy=False)
    picture = fields.Binary(related='label_type.picture', string='Picture',store=True)
