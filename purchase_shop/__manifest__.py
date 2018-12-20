# -*- coding: utf-8 -*-


{
    'name': 'Purchase in shop',
    'version': '9.0.0.1.0',
    'summary': 'Adapt purchase order for direct shop purchase',
    'author': "David Bertha",
    'license': 'AGPL-3',
    'depends': ['purchase', 'point_of_sale'],
    'data': [
        'purchase_shop.xml',
        'security/purchase_shop_security.xml'
        ],
    #'demo': ['pos_payment_terminal_demo.xml'],
    #'qweb': ['static/src/xml/pos_second_cashier.xml'],
    'installable': True,
}
