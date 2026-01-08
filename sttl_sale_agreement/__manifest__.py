{
    'name': 'Sales Agreement',
    'version': '18.0.1.0',
    'category': 'Tools',
    'summary': 'Sales Agreement',
    'description': """
        This module provides functionality of Sales Agreement
    """,
        "depends": [
        "sale",
        "sale_management",
    ],
 
    'data': [
        "security/ir.model.access.csv",
        'data/sales_quotation_sequence_data.xml',
        'views/sale_action_views.xml',
        "views/sales_agreement_menus.xml",
        "views/sale_requasition_view.xml",
        "views/sale_order_views.xml"
    ],
    'installable': True,
    'license': 'LGPL-3',
    "author": "Silver Touch Technologies Limited",
    "website": "https://www.silvertouch.com/",
    'images': ['static/description/icon.png'],
}
