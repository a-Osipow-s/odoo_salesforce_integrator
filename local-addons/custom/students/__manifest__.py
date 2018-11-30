# -*- coding: utf-8 -*-
{
    'name': "Students",

    'summary': """Manage students""",

    'description': """
        Students module for managing studentss:
            - create students
    """,

    'author': "Matvey",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'queue_job'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'views/students.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}