# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Webpage for barcode scanning',
    'version' : '2.1',
    'summary': 'web form to scan barcode and create picking for restaurant',
    'sequence': 30,
    'description':"Barcode scanning of products using webform for creating auto restaurant inter picking",
    'category': 'web',
    'depends' : ['base','stock','barcodes','website'],
    'data': [
#        'security/ir.model.access.csv',
        'views/res_users_view.xml',
        'views/barcode_scan.xml',
        'views/webform_view_template.xml',
        'views/restaurant_picking_config_view.xml',
        'views/restaurant_picking_scheduler.xml',
        
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,

}
