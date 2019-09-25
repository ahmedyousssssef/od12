# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    fixed_salary = fields.Float(string="Fixed social insurance",  required=False, )
    variable_salary = fields.Float(string="Variable social insurance",  required=False, )
    net_salary = fields.Float(string="Net Salary",  required=False, )
    freelancer_loc = fields.Float(string="Freelancer Local",  required=False, )
    freelancer_inter = fields.Float(string="Freelancer International",  required=False, )
    additional = fields.Float(string="Gross",  required=False, )
    wage = fields.Float(string="Basic", digits=(16, 2), required=True, help="Basic Salary of the employee")
