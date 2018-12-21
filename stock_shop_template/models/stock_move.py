from odoo import models, fields, api

class StockMove(models.Model) :
	# _name = 'stock.move'
	_inherit = 'stock.move'
        
        #check move created from Template Cron
	temp_create_move = fields.Boolean('Template Created Move')
	becoming_late = fields.Boolean('Becoming late')