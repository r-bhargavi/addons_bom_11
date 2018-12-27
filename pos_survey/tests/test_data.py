# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.addons.pos_survey.tests.test_data import TestData

from odoo import fields
import logging
_logger = logging.getLogger(__name__)
import odoo
import odoo.tests
@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)


class ClosePosSession(TestData):
  
    def test_close_pos_session(self):
        currency_id = self.env['res.currency'].create({
            'name':'usd',
            'symbol':'$'
            })
        company_id = self.env['res.compnay'].create({
            'name':'Test Compnay',
            'currency_id':currency_id.id
            })
        user_id = self.env['res.user'].create({
            'name':'test user',
            'login''a'
            })
        servye_id = self.env['survey.survey'].create({
            'titel':'Test Servey'
            })
        print ("\n\n servey id=======",servye_id)
        session_id = self.env['pos.session'].create({
            'user_id':user_id.id,
            'config_id':1
            })
        servey_user_input_id = self.env['survey.user_input'],create({
            'servey_id':servey_id,
            'session_id':session_id.id
            })
        account_journal_id = self.env['account.journal'].create({
            'name':'bank',
            'type':'sale',
            'code':'Bank'
            })
        servey_quetion_id = self.env['survey.question'].create({
            'quetion':'Test Quetion',
            'survey_id':servey_id.id,
            'journal_ids':account_journal_id.id
            })
        
        #write method flow of servey.user_input
        if servey_user_input_id.state == 'done':
            if servey_user_input_id.session_id and servey_user_input_id.session_id.state != 'closed':
                session_id.action_pos_session_closing_control()
                session_id.action_pos_session_close()

        # action servey user input method flow
        user_input = self.env['survey.user_input'].browse(servey_user_input_id.id)
        questions_to_fill = self.env['survey.question'].search([('survey_id', '=', servye_id.id),('journal_ids', '!=', False)])
        for question in questions_to_fill:
            for journal in question.journal_ids :
                if journal.id in self.statement_ids.mapped('journal_id').mapped('id') :
                        statement = session_id.statement_ids.filtered(lambda x : x.journal_id.id == journal.id)
                        vals = {
                            'user_input_id': user_input.id,
                            'question_id': question.id,
                            'page_id': question.page_id.id,
                            'survey_id': question.survey_id.id,
                            'skipped': False,
                            'answer_type' : 'number',
                            'value_number' : statement.total_entry_encoding
                        }
                        user_input_line =  self.env['survey.user_input_line'].search([('user_input_id', '=', servey_user_input_id.id),('question_id', '=', servey_quetion_id.id)])
                        if not user_input_line :
                            self.env['survey.user_input_line'].create(vals)
                        else : #updatebecause session could have been updated
                            user_input_line.write(vals)