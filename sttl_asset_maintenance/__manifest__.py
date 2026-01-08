# -*- coding: utf-8 -*-

{
    'name': 'Asset Maintenance',
    'version': '18.0.1.0',
    'category': 'Tools',
    'summary': 'Asset Maintenance',
    'description': """
        Asset Maintenance
    """,
    'depends': [
        'base',
        'product',
        'stock',
        'helpdesk',
        'repair',
        'sttl_assets',
        'sttl_repair_sign_modification',
        'helpdesk_repair',
        "web_gantt",
        "maintenance",
        "hr",
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/maintenance_sequence.xml',
        'views/product_template.xml',
        'views/stock_picking_views.xml',
        'views/maintenance_request_views.xml',
        'views/maintenance_frequency_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_team_views.xml',
        'views/stock_lot_views.xml',
        'views/maintenance_stage_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/helpdesk_stage_views.xml',

        'wizard/maintenance_sign_wizard.xml',
        'wizard/maintenance_request_wizard.xml',
        'wizard/stock_return_picking_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    "author": "Silver Touch Technologies Limited",
    "website": "https://www.silvertouch.com/",
}
