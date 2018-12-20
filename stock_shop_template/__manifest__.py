# -*- coding: utf-8 -*-
{
    'name': "stock_shop_template",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase_shop','website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/picking_template_wizard_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/picking_temp_seq_view.xml',
        'views/product_view.xml',
        'views/picking_template_view.xml',
        'views/cron.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}