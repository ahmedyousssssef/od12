# -*- coding: utf-8 -*-

from odoo import models, fields, api
from itertools import groupby


class WorkingTime(models.Model):
    _inherit = 'resource.calendar'

    public_holiday_ids = fields.One2many('hr.public.holiday', 'holiday_id', string='Public Holidays')
    weekend_ids = fields.Many2many(comodel_name="weekend.days",string="WeekEnd Days")
    work_period = fields.Float(string="Work Period",compute='_get_working_hour',  required=False, )
    attendance_id = fields.Many2one(comodel_name="hr.attendance.structure", string="Attendance Rule", required=False, )


    @api.one
    @api.depends('attendance_ids.hour_from','attendance_ids.hour_to')
    def _get_working_hour(self):
        interval_data = []
        hours = 0.0
        working_intervals_on_day = self.get_working_intervals_of_day()
        for interval in working_intervals_on_day:
            interval_data.append(interval)
        for interval in interval_data:
            hours += (interval[1] - interval[0]).total_seconds() / 3600.0
        if not hours:
            self.work_period = 8.0
        else:
            self.work_period = hours







class WeekEndDays(models.Model):
    _name = 'weekend.days'
    _rec_name = 'dayofweek'
    dayofweek = fields.Selection([
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ], 'Day of Week', required=True, index=True, default='Monday')
