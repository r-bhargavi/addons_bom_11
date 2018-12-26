# -*- coding: utf-8 -*-
{
    'name': "POS Survey",

    'summary': """
       """,

    'description': """
        
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale','survey'],

    # always loaded
    'data': [
         # 'security/ir.model.access.csv',
        'views/survey_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}