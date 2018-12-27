
from odoo import api, fields, models, _
import logging
from odoo import SUPERUSER_ID


_logger = logging.getLogger(__name__)

#to maintain product ingredients max length and picture

class LabelType(models.Model):
    _name='label.type'
    _rec_name='name'
    
    name=fields.Char(string='Name',requires=True, copy=False)
    max_length=fields.Integer(string='Max Length Ingredients',requires=True, copy=False)
    picture = fields.Binary('Picture', attachment=True)
    
    
