# -*- coding: utf-8 -*-
{
    "name": "Sale Quantity Forecast Report",
    "version": "18.0.1.0",
    "author": "Silver Touch Technologies Limited",
    'category': 'sale',
    "website": "https://www.silvertouch.com/",
    "summary": "Purchase Report",
    "description": """
            Sale Quantity forecast Report
        """,
    'depends': ['sale', 'sale_stock','sale_management'],
    'data': [
        "views/sale_reports.xml",
        "views/so_quantity_forecast.xml",
        "views/res_partner.xml"
    ],
    "license": "LGPL-3",
    'installable': True,
}
