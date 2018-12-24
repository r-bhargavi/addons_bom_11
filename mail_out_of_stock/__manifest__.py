# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Mail Out of Stock Schedular',
    'version' : '1.1',
    'summary': 'Sends Mail if Product Out of Stock',
    'sequence': 30,
    'author':'Knacktechs Solutions',
    'category': 'Custom Addons',
    'website': 'https://www.knacktechs.com/',
    'depends' : ['base', 'stock', 'product'],
    'data': [
            'views/scheduler.xml',
            'views/template.xml',
            'views/mail_template_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
