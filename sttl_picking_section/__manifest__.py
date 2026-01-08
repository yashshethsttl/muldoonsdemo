# -*- coding: utf-8 -*-

{
    'name': 'Stock Section',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Stock Section',
    'description': """

    """,
    "author": "Silver Touch Technologies Limited",
    "website": "https://www.silvertouch.com/",
    'depends': ['stock', 'sale', 'account', 'web'],
    'data': [
        'report/report_delivery_slip.xml',
        'views/stock_picking_views.xml',
        'report/stock_reports.xml',
        'report/report_picking_operations.xml',
    ],
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'sttl_picking_section/static/src/js/section_widget.js',
            'sttl_picking_section/static/src/xml/list_renderer.xml',
        ],
    },
    'license': 'LGPL-3',
}
