# -*- coding: utf-8 -*-

{
    'name': 'STTL Muldoons Extended',
    'version': '18.0.1.0',
    'category': 'Tools',
    'summary': 'This module is for Muldoons customizations',
    'description': """
        This module includes all the customizations done for Muldoons Coffee.
    """,
    'depends': [
        'sale_management',
        'sale',
        'stock',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    "author": "Silver Touch Technologies Limited",
    "website": "https://www.silvertouch.com/",
}
