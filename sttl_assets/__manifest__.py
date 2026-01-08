# -*- coding: utf-8 -*-

{
    "name": "Assets",
    "version": "18.0.1.0",
    "author": "Silver Touch Technologies Limited",
    'category': '',
    "website": "https://www.silvertouch.com/",
    "description": """
        """,
    'depends': ['stock', 'product', 'account_asset', 'web', 'repair', 'project', 'maintenance', 'sttl_repair_sign_modification'],
    'data': [
        "data/stock_tracebility_report_data.xml",
        "security/ir.model.access.csv",
        "views/stock_lot.xml",
        "views/res_partner.xml",
        "views/project_task.xml",
        "views/product_template.xml",
        "views/site_report.xml",
        "views/stock_move_line_views.xml",
        "views/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sttl_assets/static/src/js/stock_tracebility_report.js',
            'sttl_assets/static/src/js/prevent_autosave_formcontroller.js',
            'sttl_assets/static/src/xml/stock_tracebility_report.xml',
        ],
    },
    "price": 0,
    "currency": "USD",
    "license": "LGPL-3",
    'installable': True,
    'application': False,
    'images': ['static/description/banner.png']
}
