# -*- coding: utf-8 -*-
{
    'name': 'Merge stock inventories',
    'version': '9.0.0.1.0',
    'summary': """If you tag an inventory as to be merged, you can create multiple inventories with same products. 
    And you can merge them before validating the stock moves
    + warning when picking qty too large (probably an error)
    + cron to remove empty pickings""",
    'author': "David Bertha",
    'license': 'AGPL-3',
    'depends': ['stock', 'stock_barcode'],
    'data': [
        'stock_inventory_merge.xml',
        'stock_inventory_merge_data.xml',
        ],
    'demo': [],
    'qweb': [],
    'installable': True,
}
