# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model) :
    _inherit = 'res.partner'

    # scheduler to send mail when partner parent is detected with multiple invoice partner type

    @api.model
    def detected_wrong_partner_configured_send_mail(self):
        self.env.cr.execute("SELECT id,parent_id from res_partner WHERE parent_id is not null and type='invoice' GROUP BY id,parent_id")
        partners = self.env.cr.fetchall()  
        values = set(map(lambda x:x[1], partners))
        child_ids = [[y[0] for y in partners if y[1]==x] for x in values]
#        email_to=template_id.email_id.ids
#        recipient_ids= [(4, pid) for pid in email_to]
        partner_details=[]
        if child_ids:
            for each in child_ids:
                if len(each)>1:
                    for each_child in self.browse(each):    
                        if each_child.parent_id.type=='invoice':
                            partner_details.append({
                            'child_name':each_child.name,
                            'parent_name':each_child.parent_id.name
                            })
                            # print "partner_detailspartner_details",partner_details
                            template_id = self.env.ref('multiple_inv_partners_mail.template_detected_multiple_inv_partners_child')
                            return template_id.with_context(details=partner_details).send_mail(each_child.parent_id.id)