# -*- coding: utf-8 -*-
{
    'name': "import_product_label",

    'summary': """
        To import Product Label Data in Odoo to be fetched henceforth to print labels""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bhargavi",
#    'website': "http://www.yourcompany.com",

    'category': 'Product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product','mrp','sale'],

    # always loaded
    'data': [
#        'security/ir.model.access.csv',
        'wizard/import_data_view.xml',
        'views/label_type_view.xml',
        'views/product_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ]
}