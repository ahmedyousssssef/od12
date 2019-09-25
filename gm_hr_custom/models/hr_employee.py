# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

# _____ Model Inherit

class hr_attendance(models.Model):
    _inherit = 'hr.employee'

    attendance_id = fields.Many2one(comodel_name="hr.attendance.structure", related='resource_calendar_id.attendance_id',
                                    string="Attendance Rule", required=False, )
    # attendance_id = fields.Many2one(comodel_name="hr.attendance.structure", related='resource_calendar_id.attendance_id',
    #                                 string="Attendance Rule", required=False, )
    job_nature_allwance_10 = fields.Float(string="Job Nature Allowance 10%")
    taxable_allowance = fields.Float(string="Taxable Allowance")
    transportation_allowance = fields.Float(string="Transportation Allowance")
    social_allowance = fields.Float(string="Social Allowance")
    special_social_allowance = fields.Float(string="Special Social Allowance")
    other_allowance = fields.Float(string="Other Allowance")
    sea_allowance10 = fields.Float(string="Sea Allowance 10%")
    job_nature_allwance_5 = fields.Float(string="Job Nature Allowance 5%")
    time_allwance_15 = fields.Float(string="Time Allowance 15%")
    representation_allwance_20 = fields.Float(string="Representation Allow. 20%")
    sea_allowance5 = fields.Float(string="Sea Allowance 5%")
    time_allwance_25 = fields.Float(string="Time Allowance 25%")
    representation_allwance_30 = fields.Float(string="Representation Allow. 30%")
    representation_allwance_15 = fields.Float(string="Representation Allow. 15%")
    representation_allwance_10 = fields.Float(string="Representation Allow. 10%")
    grade_allowance = fields.Float(string="Grade Allowance")
    correction = fields.Float(string="Correction")
    add_rewards = fields.Float(string="Rewards")
    add_profit = fields.Float(string="Profits")
    add_bonus = fields.Float(string="Bonus")




