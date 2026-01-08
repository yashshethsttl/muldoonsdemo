# -*- coding: utf-8 -*-
{
    "name": "Sttl Payslip Modification",
    "version": "18.0.1.0",
    "category": "Tools",
    "summary": "Payslip Modification",
    "description": "Payslip Modification.",
    "author": 'Silver Touch Technologies Limited',
    "website": "https://www.silvertouch.com",
    "depends": ["hr_payroll", "hr_contract"],
    "data": [
        "views/report_payslip.xml",
        "views/hr_contract_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
    'images': ['static/description/icon.png'],
}
