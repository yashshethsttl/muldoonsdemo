# -*- coding: utf-8 -*-
{
    "name": "Packaging Modification",
    "version": "18.0.1.0",
    "author": "Silver Touch Technologies Limited",
    'category': 'stock',
    "website": "https://www.silvertouch.com/",
    "summary": "Packaging Modification",
    "description": """
            Packaging Modification
        """,
    'depends': ['stock', 'stock_account','purchase','sale'],
    'data': [
        "views/stock_picking.xml",
        "views/stock_move_line.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sttl_packaging_modification/static/src/components/main.js',
            'sttl_packaging_modification/static/src/components/main.xml',
        ]
    },
    "license": "LGPL-3",
    'installable': True,
}
