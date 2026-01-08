# -*- coding: utf-8 -*-

{
    "name": "Repair Sign Modification",
    "version": "18.0.1.0",
    "author": "Silver Touch Technologies Limited",
    'category': 'helpdesk',
    "website": "https://www.silvertouch.com/",
    "description": """
        """,
    'depends': ['helpdesk', 'repair', 'stock_picking_batch', 'web_gantt'],
    'data': [
        "security/ir.model.access.csv",
        "views/repair_order.xml",
        "views/stock_picking_views.xml",
        "views/stock_picking_to_batch_views.xml",
        "views/stock_add_to_wave_views.xml",
        "views/stock_warehouse.xml",
        "views/helpdesk_menus.xml",
        "reports/repair_templates_repair_order.xml",
        "wizard/repair_sign_wizard.xml",
    ],
    "price": 0,
    "currency": "USD",
    "license": "LGPL-3",
    'installable': True,
    'application': False,
    'images': ['static/description/banner.png']
}
