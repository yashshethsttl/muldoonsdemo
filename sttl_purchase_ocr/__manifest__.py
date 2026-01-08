# -*- coding: utf-8 -*-

{
    'name': 'Purchase Order OCR',
    'version': '18.0.1.0',
    'category': 'Tools',
    'summary': 'Purchase Order OCR',
    'description': """
        Purchase Order OCR
    """,
    'depends': [
        'web',
        'purchase',
    ],
    'data': [
        'views/purchase_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sttl_purchase_ocr/static/src/components/purchase_file_uploader/purchase_file_uploader.js',
            'sttl_purchase_ocr/static/src/components/purchase_file_uploader/purchase_file_uploader.xml',
            
            'sttl_purchase_ocr/static/src/views/purchase_order_list/purchase_order_list_controller.js',
            'sttl_purchase_ocr/static/src/views/purchase_order_list/purchase_order_list_view.js',
        ]
    },
    'installable': True,
    'license': 'LGPL-3',
    "author": "Silver Touch Technologies Limited",
    "website": "https://www.silvertouch.com/",
}
