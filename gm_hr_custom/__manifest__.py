# -*- coding: utf-8 -*-
{
    'name': "Hr Customization",

    'summary': """
        HR CUSTOMIZATION""",

    'description': """
        HR CUSTOMIZATION
    """,

    'author': "Youssef",
    'website': "http://www.g2m.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'hr', 'hr_holidays', 'hr_attendance', 'hr_contract', 'resource', 'hr_holidays',
                'hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'datas/hr_data.xml',
        'views/res_config_view.xml',
        'views/mail_templates.xml',
        'views/hr_contract_view.xml',
        'report/report.xml',
        'report/contract_view_report.xml',
        'views/working_time_view.xml',
        'views/public_holiday_view.xml',
        'views/hr_attendance.xml',
        'views/hr_attendance_bonus_view.xml',
        'views/hr_attendance_deduction_view.xml',
        'views/hr_attendance_structure.xml',
        'views/hr_employee_view.xml',
        'views/attendance_rule_view.xml',
        'wizard/working_wizard_view.xml',
    ],
'application':True,
}