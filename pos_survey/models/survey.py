# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import uuid
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



# class survey(models.Model) :
#     _inherit = 'survey.survey'
#
#     access_token = fields.Char(
#         'Security Token', copy=False, default=lambda self: str(uuid.uuid4()),
#         required=True)

class survey_question(models.Model) :
    _inherit = 'survey.question'

    journal_ids =fields.One2many('account.journal', 'question_id', string="Journals")


class survey_question(models.Model) :
    _inherit = 'account.journal'

    question_id=fields.Many2one('survey.question', string="Question rapport de trésorerie")

class survey_user_input(models.Model) :
    _inherit = 'survey.user_input'
    
    session_id=fields.Many2one('pos.session', string="Session")

    @api.multi
    def write(self, vals):
        res = res = super(survey_user_input, self).write(vals)
        if 'state' in vals and vals['state'] == 'done' :
            for user_input in self.sudo() :
                if user_input.session_id and user_input.session_id.state != 'closed' :
                    # user_input.session_id.wkf_action_closing_control()
                    # user_input.session_id.wkf_action_close()
                    user_input.session_id.action_pos_session_closing_control()
                    user_input.session_id.action_pos_session_close()

    # access_token = fields.Char(
    #     'Security Token', copy=False, default=lambda self: str(uuid.uuid4()),
    #     required=True)
    
    #closs pos session and write survey in account bank statement line
    @api.multi
    def action_close_session(self):
        if self.session_id and self.user_input_line_ids and self.session_id.statement_ids:
            for line in self.user_input_line_ids:
                # self.session_id.statement_ids.filtered(lambda statement_line: statement_line.journal_id.id==line.question_id.journal_ids[0].id).write({'survey_input_line_id':line.id})
                #new code for above line
                for each in self.session_id.statement_ids:
                    for each_que in line.question_id.journal_ids:
                        if each.journal_id.id == each_que.id:
                            each.write({'survey_input_line_id':line.id})
    
    # close pos session and post or validate order
    #         self.session_id.wkf_action_closing_control()
    #         self.session_id.wkf_action_close()
            self.session_id.action_pos_session_closing_control()
            self.session_id.action_pos_session_close()
    # move survey in done state
            self.write({'state':'done'})
            
# class survey_user_input_line(models.Model) :
#     _inherit = 'survey.user_input_line'
    
#     # Add domain depending on  bank account statement journal
#     @api.onchange('question_id')
#     def onchange_question_id(self):
#         result = {}
#         if not self.user_input_id.session_id.statement_ids:
#             return result
#         journal_id=[statement_line.journal_id.id for statement_line in self.user_input_id.session_id.statement_ids]
#         result['domain'] = {'question_id': [('journal_id', 'in', [statement_line.journal_id.id for statement_line in self.user_input_id.session_id.statement_ids])]}
#         for statement_line in self.user_input_id.session_id.statement_ids:
#             if statement_line.journal_id == self.question_id.journal_id:
#                 self.value_number= statement_line.total_entry_encoding
#         return result
                
class pos_session(models.Model) :
    _inherit = 'pos.session'
    survey_id= fields.Many2one('survey.survey', string='Survey', related='config_id.survey_id')
    #open input survey form 
    @api.multi
    def action_survey_user_input(self):
        # survey_id=self.env['survey.survey'].create({'title':'Survey POS Session: '+self.name})
        # form_view_id = self.env.ref('survey.survey_user_input_form').id
        # return {
        #         'name':'Survey User Input',
        #         'context' : {'default_session_id': self.id,'default_survey_id':survey_id.id},
        #         'res_model':'survey.user_input',
        #         'view_type':'form',
        #         'views': [(form_view_id, 'form')],
        #         'type':'ir.actions.act_window',
        #        }\
        if self.config_id.survey_id:
            survey=self.config_id.survey_id
            # user_input = self.env['survey.user_input'].search([('survey_id', '=', survey.id),('session_id', '=', self.id)])
            user_input = self.env['survey.user_input'].browse(1)
            if not user_input :
                user_input = self.env['survey.user_input'].create({'survey_id':survey.id, 'session_id' : self.id})
            questions_to_fill = self.env['survey.question'].search([('survey_id', '=', survey.id),('journal_ids', '!=', False)])
            # questions_to_fill = self.env['survey.question'].browse(1)
            for question in questions_to_fill :
                for journal in question.journal_ids :
                    if journal.id in self.statement_ids.mapped('journal_id').mapped('id') :
                        statement = self.statement_ids.filtered(lambda x : x.journal_id.id == journal.id)
                        _logger.debug(statement)
                        vals = {
                            'user_input_id': user_input.id,
                            'question_id': question.id,
                            'page_id': question.page_id.id,
                            'survey_id': question.survey_id.id,
                            'skipped': False,
                            'answer_type' : 'number',
                            'value_number' : statement.total_entry_encoding
                        }
                        user_input_line =  self.env['survey.user_input_line'].search([('user_input_id', '=', user_input.id),('question_id', '=', question.id)])
                        if not user_input_line :
                            self.env['survey.user_input_line'].create(vals)
                        else : #updatebecause session could have been updated
                            user_input_line.write(vals)
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': '/survey/fill/%s/%s' % (survey.id, user_input.token),
                # 'res_id': self.config_id.survey_id.id,
                # 'url': '/survey/fill/%s/%s' % (survey.id, user_input.access_token)
            }
        else:
            raise UserError(_("Survey ID Required."))


class account_bank_statement(models.Model) :
    _inherit = 'account.bank.statement'
    
    survey_input_line_id=fields.Many2one('survey.user_input_line', string="Survey Input Line")


class pos_config(models.Model) :
    _inherit = 'pos.config'

    survey_id=fields.Many2one('survey.survey', string='Rapport de trésorerie')