# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sale Warning',
    'version' : '1.1',
    'summary': 'Warning when requested date selected is date before current date',
    'sequence': 30,
    'author':'Knacktechs Solutions',
    'category': 'Custom Addons',
    'website': 'https://www.knacktechs.com/',
    'depends' : ['base', 'sale','sale_order_dates'],
    'data': [
        'data/cron.xml',
        'views/sale_view.xml',
        'views/template.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
