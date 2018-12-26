# -*- coding: utf-8 -*-
{
    'name' : 'Website and POS',
    'version' : '1.1',
    'summary': '',
    'sequence': 30,
    'author':'Knacktechs Solutions',
    'category': 'Custom Addons',
    'website': 'https://www.knacktechs.com/',
    'description':"""To make product variants unavailable on Point of Sale and to unpublish product variants on website""",

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'website_sale','point_of_sale'],

    # always loaded
    'data': [
        'views/product_view.xml',
        'views/pos_template.xml',
    ],

}