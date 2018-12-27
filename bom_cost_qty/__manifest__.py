# -*- coding: utf-8 -*-


{
    'name': 'Bom Cost Report with quantity selection',
    'version': '9.0.0.1.0',
    'summary': 'Add wizard to choose quantity before printing the report',
    'author': "David Bertha",
    'license': 'AGPL-3',
    'depends': ['mrp','hr'],
    'data': [
        'bom_cost_qty.xml',
        'mrp_bom_inherit.xml',
        ],
    #'demo': ['pos_payment_terminal_demo.xml'],
    #'qweb': ['static/src/xml/pos_second_cashier.xml'],
    'installable': True,
}
