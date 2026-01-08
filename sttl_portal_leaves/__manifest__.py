# -*- coding: utf-8 -*-
{
    "name": "Portal Time Off",
    "version": "18.0.1.0",
    "author": "Silver Touch Technologies Limited",
    'category': 'hr',
    "summary": "",
    "website": "https://www.silvertouch.com/",
    "description": """
        """,
    'depends': ['hr_holidays', 'portal', 'hr'],
    'data': [
        'views/portal_templates.xml',
        'views/portal_leave_views.xml',
        'views/hr_employee.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            'sttl_portal_leaves/static/src/css/style.css',
            'sttl_portal_leaves/static/src/js/leave_script.js',
            'sttl_portal_leaves/static/src/js/attachment_condition.js',
        ]
    },
    "price": 0,
    "currency": "USD",
    "license": "LGPL-3",
    'installable': True,
    'application': False,
    'images': ['static/description/banner.png']
}
