# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from datetime import datetime, time, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)

class MrpBom(models.Model):
    _inherit='mrp.bom'

    employee_id=fields.Many2one('hr.employee', string='Employee')
    validation_date=fields.Date(string='Validation Date')