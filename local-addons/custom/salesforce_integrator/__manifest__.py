# -*- coding: utf-8 -*-
{
    'name': "Salesforce integrator",

    'summary': """Integrate salesforce""",

    'description': """
        Module for integrate salesforce
    """,

    'author': "Matvey",
    'website': "http://www.yourcompany.com",

    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'queue_job'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}