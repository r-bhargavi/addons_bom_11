# -*- coding: utf-8 -*-


import json
import logging
import werkzeug
import werkzeug.utils
from datetime import datetime
from math import ceil

from odoo import SUPERUSER_ID
from odoo.addons.web import http
from odoo.addons.web.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DTF, ustr


_logger = logging.getLogger(__name__)

import odoo.addons.survey.controllers.main


class WebsiteSurvey(openerp.addons.survey.controllers.main.WebsiteSurvey):
    # AJAX submission of a page
    @http.route(['/survey/submit/<model("survey.survey"):survey>'],
                type='http', methods=['POST'], auth='public', website=True)
    def submit(self, survey, **post):
        print ("\n\n call---------------")
        _logger.debug("in overloaded controller")
        res = super(WebsiteSurvey, self).submit(survey,**post)
        user_input_id = self.env['survey.user_input_line'].search([('token', '=', post['token'])])
        _logger.debug(user_input_id)
        _logger.debug(post)
        if user_input_id and user_input_id.state == 'done' and user_input_id.session_id and user_input_id.session_id.state != 'closed' :
            user_input_id.session_id.wkf_action_closing_control()
            user_input_id.session_id.wkf_action_close()
        return res