# __manifest__.py
{
    'name': 'Vendor Bill Digitalisation',
    'version': '18.0',
    'category': 'Tools',
    "author": "Silver Touch Technologies Limited",
    "website": "https://www.silvertouch.com/",
    'summary': 'Extracts the information from the vendor bills in image or pdf formatt and creates bill.',
    'depends': ['base', 'web', 'account', 'base_setup'],
    'assets': {
    },
    'data': [
        'views/res_config_view.xml',
    ],
    'images': ['static/description/banner_youtube.png'],
    'installable': True,
    'application': True,
}
