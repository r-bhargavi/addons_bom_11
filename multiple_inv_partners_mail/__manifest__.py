# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Scheduler to Send Mail for Wrongly Configured Partner',
    'version' : '1.1',
    'summary': 'Sends Mail if Wrongly Configured Partner Detected',
    'sequence': 30,
    'author':'Bhargavi',
    'category': 'Custom Addons',
    'website': '',
    'depends' : ['base','mail'],
    'data': [
            'views/scheduler.xml',
            'views/template.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
