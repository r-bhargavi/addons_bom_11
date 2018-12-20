from openerp import models, fields, api,_
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import calendar
import re

import logging
from openerp import SUPERUSER_ID


_logger = logging.getLogger(__name__)

TEMPLATE_FLAG = "[template]"

class StockPickingTemplate(models.Model):
    _name='stock.picking.template'
    _rec_name='name'

    name=fields.Char(string='Name',required=True, copy=False, readonly=True, index=True, compute='_compute_name')
    picking_type=fields.Many2one('stock.picking.type', string='Picking Type')
    temp_date=fields.Date('Template Date', default=fields.Date.today())
    week_days=fields.Selection([
        ('Sunday', 'Sunday'),
        ('Monday','Monday'),
        ('Tuesday','Tuesday'),
        ('Wednesday','Wednesday'),
        ('Thursday','Thursday'),
        ('Friday','Friday'),
        ('Saturday','Saturday')], string='Day of Week')
    src_location=fields.Many2one('stock.location', string='Source Location')
    dest_location=fields.Many2one('stock.location', string='Destination Location')
    partner_id=fields.Many2one('res.partner', string='Partner')
    temp_category=fields.Char(string='Category')
    temp_lines=fields.One2many('stock.picking.template.line','pick_temp_id', string='Template Lines', copy=True)

    company_id=fields.Many2one('res.company', string='Company',default=lambda self: self.env['res.company']._company_default_get('stock.picking.template'))

    @api.depends('week_days', 'temp_category', 'dest_location')
    def _compute_name(self):
        for temp in self:
            temp.name = "[%s][%s][%s]" % (temp.dest_location.location_id.name, temp.week_days, temp.temp_category)

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         if 'company_id' in vals:
    #             vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
    #                 'stock.picking.template') or _('New')
    #         else:
    #             vals['name'] = self.env['ir.sequence'].next_by_code('stock.picking.template') or _('New')
    #     result=super(StockPickingTemplate, self).create(vals)
    #     return result

    # def get_current_week_number(self):
    #     cal = calendar.Calendar()
    #     current_year = datetime.strftime(datetime.today(), '%Y')
    #     current_month=datetime.strftime(datetime.today(),'%M')
    #     print"current_monthcurrent_monthcurrent_monthcurrent_month", current_month, current_year
    #     total_weeks=len(cal.monthdays2calendar(current_year, current_month))
    #     print"total_weekstotal_weekstotal_weekstotal_weeks", total_weeks
    # cron function to create pickings from template
    @api.model
    def _cron_generate_provision(self):
        day=''
        product_obj = self.env['product.product']
        day_today = date.today().weekday()
        week_day=calendar.day_name[day_today]
        _logger.debug(week_day)
        day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        day_names_eng =['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day = day_names[day_today]
        # if week_day=='Monday':
        #     day='Lundi'
        # elif week_day=='Tuesday':
        #     day='Mardi'
        # elif week_day=='Wednesday':
        #     day='Mercredi'
        # elif week_day=='Thursday':
        #     day='Jeudi'
        # elif week_day=='Friday':
        #     day='Vendredi'
        # elif week_day=='Saturday':
        #     day='Samedi'
        # else:
        #     day='Dimanche'
        # check and cancel pickings which are in draft state
        pending_picking_ids = self.env['stock.picking'].search([('state', '=', 'draft'), ('temp_create_pick', '=', True), ('origin', 'not ilike', day)])
        if pending_picking_ids:
            for pick_id in pending_picking_ids:
                pick_id.action_cancel()
        # to create pickings from template which has today's day
        temp_picking_ids = self.search([('week_days', 'in', [day_names_eng[day_today], day_names_eng[(day_today + 1) % 7]])])
        if temp_picking_ids:
            for temp_picking in temp_picking_ids:
                _logger.debug(temp_picking)
                template_lines=[]
                # weekNumber = date.today().isocalendar()[1]
                # to get current week number of month from date
                week_date = date.today()
                current_week_number = (self.env['product.template'].get_current_week() % 4) + 1 #from 1 to4 for instead of 0 to 3 
                #get next week as the picking will be generated before the rotation
                # current_week_number=3
                for line in temp_picking.temp_lines:
                    # to check week number in product matches with current week number
                    if line.product_id.active and (not line.product_id.product_tmpl_id.week_number or (line.product_id.product_tmpl_id.week_number and int(line.product_id.product_tmpl_id.week_number)==current_week_number)):
                        tmp_lines={
                            'product_id':line.product_id.id,
                            'name': line.product_id.partner_ref,
                            'product_uom_qty':line.suggested_qty,
                            'product_uom': line.product_id.uom_id.id,
                            'location_id':
                                temp_picking.src_location.id or
                                self.env.ref('stock.stock_location_stock').id,
                            'location_dest_id':
                                temp_picking.dest_location.id or
                                self.env.ref('stock.stock_location_customers').id,
                        }
                    # to check whether picking_uom_id is there on product or not
                        if line.product_id.picking_uom_id:
                            tmp_lines.update({'product_uom':line.product_id.picking_uom_id.id})
                        template_lines.append((0,0,tmp_lines))
                # day_picking = datetime.strptime(temp_picking.temp_date, DEFAULT_SERVER_DATETIME_FORMAT).weekday()
                # if day_today == day_picking:
                vals={
                    'partner_id':temp_picking.partner_id.id,
                    'location_id':temp_picking.src_location.id,
                    'location_dest_id':temp_picking.dest_location.id,
                    'picking_type_id':temp_picking.picking_type.id,
                    'origin':'['+str(temp_picking.dest_location.location_id.name)+']'+'['+day_names[day_names_eng.index(temp_picking.week_days)]+']'+'['+str(temp_picking.temp_category)+']',
                    'move_lines': (template_lines)
                }
                #Do not create if already created yesterday
                if not self.env['stock.picking'].search(['|' , ('state', 'in', ('draft', 'confirmed','partially_available','assigned' )),
                 '&', '&', ('merged', '=', True), ('state', '=', 'cancel'), ('create_date', '>', (date.today() - timedelta(days=2)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('temp_create_pick', '=', True), ('origin', '=', vals['origin']), ('move_lines', '!=', False)]) :
                #orders for today created yesterday and merged should not be generated again
                    _logger.debug(vals)
                    if vals['move_lines']!=[]:
                        new_picking=self.env['stock.picking'].create(vals)
                        # print "new picking in generate provioson------",new_picking.origin
                        if new_picking:
                            new_picking.temp_create_pick = True
                            new_picking.operating_unit_id = None
                            temp_picking.is_picking_created=True
                            # reset picking company by destination company if picking generate through cron
                            new_picking.company_id = temp_picking.dest_location.company_id.id
                            if temp_picking.week_days == day_names_eng[day_today] :
                                new_picking.min_date = date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            else :
                                new_picking.min_date = (date.today() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            for move_line in new_picking.move_lines:
                                move_line.temp_create_move = True
                                move_line.company_id = temp_picking.dest_location.company_id.id


    @api.multi
    def fetch_pickings(self):
        picking_ids=self.env['stock.picking'].search([('origin', 'ilike', TEMPLATE_FLAG), ('state', "=", 'draft')])
        if picking_ids:
            for picking in picking_ids:
                picking_date=datetime.strptime(picking.min_date, "%Y-%m-%d %H:%M:%S")
                day_no=picking_date.weekday()
                week_day=calendar.day_name[day_no]
                template_lines = []
                for line in picking.move_lines:
                    temp_lines=(0,0,{
                        'product_id':line.product_id.id,
                        'suggested_qty':line.product_uom_qty
                    })
                    template_lines.append(temp_lines)
                final_lst=re.findall("\[(.*?)\]", picking.origin)
                category=final_lst [-1]
                vals={
                    'partner_id': picking.partner_id.id,
                    'src_location':picking.location_id.id,
                    'dest_location': picking.location_dest_id.id,
                    'picking_type':picking.picking_type_id.id,
                    'temp_lines':template_lines,
                    'week_days':str(week_day),
                    'temp_category':category
                }
                new_pick_temp_id=self.env['stock.picking.template'].create(vals)
                if new_pick_temp_id:
                    picking.action_cancel()

class StockPickingTempLine(models.Model):
    _name='stock.picking.template.line'

    pick_temp_id=fields.Many2one('stock.picking.template', copy=False, ondelete='cascade')
    product_id=fields.Many2one('product.product', string='Product')
    suggested_qty=fields.Float(string='Suggested Quantity')
    product_uom_id=fields.Many2one('product.uom', string='Unit of Measure', related='product_id.picking_uom_id')

