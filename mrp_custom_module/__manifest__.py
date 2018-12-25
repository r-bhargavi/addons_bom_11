# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Product Variants',
    'summary': 'View and create wizards',
    'category': 'Product',
    'description': """
Accounting Reports
====================
    """,
    'depends': ['product','mrp'],
    'data': [
        'report/mail_template.xml',
        'views/inherit_product_view.xml',
        'views/add_product_variants.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_backend.xml',
    ],
    'auto_install': True,
    'installable': True,
    'license': 'OEEL-1',
}
