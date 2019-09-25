# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import time
from pytz import timezone
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


# ________________________________________________ Model Inherit

class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    late = fields.Float(string='Late Check In', compute='_compute_late',)
    early = fields.Float(string='Early Check Out', compute='_compute_early',)
    over_time = fields.Float(string='Over Time', compute='_compute_over_time',)
    # over_time_amount = fields.Float(string='Over Time Amount', compute='_compute_over_time', store=True)
    # over_time_hour = fields.Float(string='Over Time Hour', compute='_compute_over_time', store=True)
    approval_one = fields.Boolean(string="Direct Manager Approval" , default=False)
    approval_sec = fields.Boolean(string="HR Manager Approval" , default=False)

    def get_time_from_float(self,float_time):
        str_time = str(float_time)
        str_hour = str_time.split('.')[0]
        str_minute = ("%2d" % int(str(float("0." + str_time.split('.')[1]) * 60).split('.')[0])).replace(' ', '0')
        minute = (float(str_hour) * 60) + float(str_minute)
        return minute

    def _get_check_time(self, check_date):
        user_id = self.env['res.users']
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        user = user_id.browse(SUPERUSER_ID)
        # tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        tz = pytz.utc
        checkdate = pytz.utc.localize(
            datetime.strptime(check_date, DATETIME_FORMAT)).astimezone(tz)
        return checkdate

    def get_work_from(self, date_in, working_hours_id):
        hour = 0.0
        if type(date_in) is datetime:
            working_hours = working_hours_id
            for line in working_hours.attendance_ids:
                if int(line.dayofweek) == date_in.weekday():
                    hour = line.hour_from
        return hour

    def get_work_to(self, date_out, working_hours_id):
        hour = 0.0
        if type(date_out) is datetime:
            working_hours = working_hours_id
            for line in working_hours.attendance_ids:
                if int(line.dayofweek) == date_out.weekday():
                    hour = line.hour_to
        return hour

    @api.one
    @api.depends('check_in')
    def _compute_late(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.check_in and self.employee_id.resource_calendar_id:
            weekend_days = [day.dayofweek for day in self.employee_id.resource_calendar_id.weekend_ids]
            check_in = self._get_check_time(self.check_in).replace(tzinfo=None)
            if check_in.strftime('%A') not in weekend_days:
                wrok_from = self.get_work_from(check_in, self.employee_id.resource_calendar_id)
                str_time = str(wrok_from)
                hour = str_time.split('.')[0]
                minte = str_time.split('.')[1]
                work_start = datetime(year=check_in.year, month=check_in.month, day=check_in.day, hour=00, minute=00) + timedelta(hours=float(hour),minutes=float(minte))
                work_start = pytz.utc.localize(datetime.strptime(str(work_start), DATETIME_FORMAT)).replace(tzinfo=None)
                if check_in > work_start:
                    dif = check_in - work_start
                    self.late =float(dif.seconds)/3600

    @api.one
    @api.depends('check_out')
    def _compute_early(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.check_out and self.employee_id.resource_calendar_id:
            weekend_days = [day.dayofweek for day in self.employee_id.resource_calendar_id.weekend_ids]
            check_out = self._get_check_time(self.check_out).replace(tzinfo=None)
            if check_out.strftime('%A') not in weekend_days:
                wrok_to = self.get_work_to(check_out, self.employee_id.resource_calendar_id)
                str_time = str(wrok_to)
                hour = str_time.split('.')[0]
                minte = str_time.split('.')[1]
                work_end = datetime(year=check_out.year, month=check_out.month, day=check_out.day, hour=00,
                                               minute=00) + timedelta(hours=float(hour), minutes=float(minte))
                work_end = pytz.utc.localize(datetime.strptime(str(work_end), DATETIME_FORMAT)).replace(tzinfo=None)

                if check_out < work_end:
                    dif = work_end - check_out
                    self.early = float(dif.seconds) / 3600

    # def _get_current_sheet(self, employee_id, date=False):
    #     if not date:
    #         date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #
    #     att_tz_date_str = self._get_attendance_employee_tz(employee_id, date=date)
    #     sheet = self.env['hr_timesheet_sheet.sheet'].search(
    #         [('date_from', '<=', att_tz_date_str),
    #          ('date_to', '>=', att_tz_date_str),
    #          ('employee_id', '=', employee_id)], limit=1)
    #     return sheet or False
    #
    #
    # def _get_attendance_employee_tz(self, employee_id, date):
    #     """ Simulate timesheet in employee timezone
    #
    #     Return the attendance date in string format in the employee
    #     tz converted from utc timezone as we consider date of employee
    #     timesheet is in employee timezone
    #     """
    #     tz = False
    #     if employee_id:
    #         employee = self.env['hr.employee'].browse(employee_id)
    #         tz = employee.user_id.partner_id.tz
    #
    #     if not date:
    #         date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #
    #     att_tz = timezone(tz or 'utc')
    #
    #     attendance_dt = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
    #     att_tz_dt = pytz.utc.localize(attendance_dt)
    #     att_tz_dt = att_tz_dt.astimezone(att_tz)
    #     # We take only the date omiting the hours as we compare with timesheet
    #     # date_from which is a date format thus using hours would lead to
    #     # be out of scope of timesheet
    #     att_tz_date_str = datetime.strftime(att_tz_dt, DEFAULT_SERVER_DATE_FORMAT)
    #     return att_tz_date_str



    #
    # @api.model
    # def create(self, vals):
    #     if self.env.context.get('sheet_id'):
    #         sheet = self.env['hr_timesheet_sheet.sheet'].browse(self.env.context.get('sheet_id'))
    #     else:
    #         sheet = self._get_current_sheet(vals.get('employee_id'), vals.get('check_in'))
    #     if sheet:
    #         att_tz_date_str = self._get_attendance_employee_tz(vals.get('employee_id'), date=vals.get('check_in'))
    #         if sheet.state not in ('draft', 'new'):
    #             raise UserError(_('You can not enter an attendance in a submitted timesheet. Ask your manager to reset it before adding attendance.'))
    #         elif sheet.date_from > att_tz_date_str or sheet.date_to < att_tz_date_str:
    #             raise UserError(_('You can not enter an attendance date outside the current timesheet dates.'))
    #     print(vals.get('employee_id').department_id , "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
    #     # recipient_partners_1 = []
    #     # for user in self.env.ref('ohrms_loan.group_finance_manager').users:
    #     #     recipient_partners_1.append(user.partner_id.id)
    #     # post_vars = {'subject': "Approval Message",
    #     #              'body': "Loan : ( " + str(self.name) + " ) Needs Your Approval . ",
    #     #              'partner_ids': recipient_partners_1}
    #     # thread_pool = self.env['mail.thread']
    #     # thread_pool.message_post(
    #     #     type="notification",
    #     #     subtype="mt_comment",
    #     #     **post_vars)
    #     return super(hr_attendance, self).create(vals)







    @api.one
    @api.depends('check_out')
    def _compute_over_time(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.check_out and self.employee_id.resource_calendar_id:
            weekend_days = [day.dayofweek for day in self.employee_id.resource_calendar_id.weekend_ids]
            check_in = self._get_check_time(self.check_in).replace(tzinfo=None)
            check_out = self._get_check_time(self.check_out).replace(tzinfo=None)
            if check_out.strftime('%A') not in weekend_days:
                wrok_to = self.get_work_to(check_out, self.employee_id.resource_calendar_id)
                str_time = str(wrok_to)
                hour = str_time.split('.')[0]
                minte = str_time.split('.')[1]
                work_end = datetime(year=check_out.year, month=check_out.month, day=check_out.day, hour=00,
                                               minute=00) + timedelta(hours=float(hour), minutes=float(minte))
                work_end = pytz.utc.localize(datetime.strptime(str(work_end), DATETIME_FORMAT)).replace(tzinfo=None)
                if check_out > work_end:
                    dif = check_out - work_end
                    self.over_time = float(dif.seconds) / 3600
            else:
                dif = check_out - check_in
                self.over_time = float(dif.seconds) / 3600

            # if self.employee_id.attendance_id.rule_bonus_ids:
            #     hour_time = 0.0
            #     amount_time = 0.0
            #
            #     time_over = self.get_time_from_float(self.over_time)
            #     for rule in self.employee_id.attendance_id.rule_bonus_ids:
            #         if rule.bonus_type == 'hour':
            #             time_from = self.get_time_from_float(rule.time_from)
            #             time_to = self.get_time_from_float(rule.time_to)
            #             if time_over >= time_from and time_over <= time_to:
            #                 hour_time += rule.bonus_hours
            #         else:
            #             start_from = self.get_time_from_float(rule.start)
            #             if time_over >= start_from:
            #                 amount_time += rule.bonus_fixed
            #     self.over_time_hour = hour_time
            #     self.over_time_amount = amount_time









