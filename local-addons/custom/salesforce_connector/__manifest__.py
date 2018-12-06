# -*- coding: utf-8 -*-
{
    'name': "Salesforce Connector",
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Odoo Salesforce',
    'author': 'Matvey',
    'website': 'http://www.yourcompany.com',
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}