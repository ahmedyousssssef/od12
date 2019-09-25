# -*- coding: utf-8 -*-

from __future__ import division

import time
from datetime import datetime, timedelta
from dateutil import relativedelta

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
from odoo import SUPERUSER_ID
import pytz


class HrPayrollRule(models.Model):
    _name = 'hr.payslip.rule'
    _rec_name = 'name'

    name = fields.Char('Description')
    code = fields.Char('Code')
    num_of_days = fields.Float(string="Number Of Days", required=False, )
    num_of_hours = fields.Float(string="Number Of Hours", required=False, )
    pay_amount = fields.Float(string="Pay Amount", required=False, )
    rule_id = fields.Many2one(comodel_name="hr.payslip", string="Payslip", required=False, )


class hr_payroll(models.Model):
    _inherit = 'hr.payslip'

    attend_rule_ids = fields.One2many(comodel_name="hr.payslip.rule", string="Attendance Rules",
                                      inverse_name='rule_id', )
    deduction_amount = fields.Float(string="Deduction Amount", required=False, compute='_compute_deduction_amount')
    overtime_amount = fields.Float(string="OverTime Amount", required=False, compute='_compute_overtime_amount')
    absent_amount = fields.Float(string="Absence Amount", required=False, compute='_compute_absent_amount')
    attend_date_from = fields.Date(string='Date From', readonly=True, required=True,
                                   default=str(datetime.now() + relativedelta.relativedelta(months=-1, day=20))[:10],
                                   states={'draft': [('readonly', False)]})

    attend_date_to = fields.Date(string='Date To', readonly=True, required=True,
                                 default=str(datetime.now() + relativedelta.relativedelta(months=0, day=19))[:10],
                                 states={'draft': [('readonly', False)]})
    is_refund = fields.Boolean(string="Refund")

    @api.multi
    def refund_sheet(self):
        for payslip in self:
            if payslip.is_refund:
                raise UserError(_('You Cannot Refund Payslip More one time.'))
            copied_payslip = payslip.copy(
                {'credit_note': True, 'is_refund': True, 'name': _('Refund: ') + payslip.name})
            payslip.update({'is_refund': True})
            copied_payslip.input_line_ids = payslip.input_line_ids
            copied_payslip.compute_sheet()
            copied_payslip.action_payslip_done()
        formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': ("Refund Payslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    @api.model
    def create(self, values):
        res = super(hr_payroll, self).create(values)
        payrolls = self.search([('employee_id', '=', res.employee_id.id)]).filtered(lambda pay: not pay.is_refund)
        for payroll in payrolls:
            if payroll.id != res.id and not res.is_refund:
                if (payroll.date_to >= res.date_from >= payroll.date_from) or (
                        payroll.date_to >= res.date_to >= payroll.date_from):
                    raise UserError(_('You Cannot Create Two Payslips for one Employee In Same Period.'))
        return res

    @api.multi
    def get_attendance_lines(self):
        for record in self:
            record.attend_rule_ids.unlink()
            f_l_h_l = s_l_h_l = t_l_h_l = fo_l_h_l = fi_l_h_l = []
            f_l_h_e = s_l_h_e = t_l_h_e = fo_l_h_e = fi_l_h_e = []
            first_hour_late = []
            second_hour_late = []
            third_hour_late = []
            four_hour_late = []
            five_hour_late = []
            first_hour_early = []
            second_hour_early = []
            third_hour_early = []
            four_hour_early = []
            five_hour_early = []
            absent_rules = []
            absent_rule_take = []
            val_absence = 0.0
            overtime_hour = 0.0
            val_deduction = 0.0
            user_id = self.env['res.users']
            attendance_obj = self.env['hr.attendance']
            holidays_obj = self.env['hr.leave']
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            user = user_id.browse(SUPERUSER_ID)
            # tz = pytz.timezone(user.partner_id.tz) or pytz.utc
            tz = pytz.utc
            def daterange(start_date, end_date):
                for n in range(int((end_date - start_date).days) + 1):
                    yield start_date + timedelta(n)

            def get_time_from_float(float_time):
                str_time = str(float_time)
                str_hour = str_time.split('.')[0]
                str_minute = ("%2d" % int(str(float("0." + str_time.split('.')[1]) * 60).split('.')[0])).replace(' ',
                                                                                                                 '0')
                minute = (float(str_hour) * 60) + float(str_minute)
                return minute

            if not record.employee_id.attendance_id:
                raise Warning(_("You Should Choose Attendance Rules on Employee"))
            if record.employee_id.attendance_id.rule_deduction_ids:
                for line in record.employee_id.attendance_id.rule_deduction_ids:
                    if line.type == 'late':
                        if line.hour_level == '1':
                            first_hour_late.append(line.id)
                        elif line.hour_level == '2':
                            second_hour_late.append(line.id)
                        elif line.hour_level == '3':
                            third_hour_late.append(line.id)
                        elif line.hour_level == '4':
                            four_hour_late.append(line.id)
                        elif line.hour_level == '5':
                            five_hour_late.append(line.id)
                    elif line.type == 'early':
                        if line.hour_level == '1':
                            first_hour_early.append(line.id)
                        elif line.hour_level == '2':
                            second_hour_early.append(line.id)
                        elif line.hour_level == '3':
                            third_hour_early.append(line.id)
                        elif line.hour_level == '4':
                            four_hour_early.append(line.id)
                        elif line.hour_level == '5':
                            five_hour_early.append(line.id)
                    else:
                        absent_rules.append(line.id)

            permission = record.employee_id.attendance_id.permission or 0.0
            search_domain = [
                ('check_in', '>=', record.attend_date_from),
                ('check_out', '<=', record.attend_date_to),
                ('employee_id', '=', record.employee_id.id),
                ('approval_one', '=', True),
                ('approval_sec', '=', True)
            ]
            hours = record.employee_id.resource_calendar_id.work_period
            attendance_ids = attendance_obj.search(search_domain)
            start_date = datetime.strptime(str(record.attend_date_from), "%Y-%m-%d")
            end_date = datetime.strptime(str(record.attend_date_to), "%Y-%m-%d")
            weekend_days = [day.dayofweek for day in record.employee_id.resource_calendar_id.weekend_ids]
            attendances = [x.check_in[0:10] for x in attendance_ids]
            for single_date in daterange(start_date, end_date):
                if str(single_date.date()) in attendances:
                    for attendance in attendance_ids:
                        attendance_datetime = pytz.utc.localize(
                            datetime.strptime(attendance.check_in, DATETIME_FORMAT)).astimezone(tz)
                        if attendance_datetime.date() == single_date.date():
                            late = 0.0
                            early = 0.0
                            if attendance.late > 0.0:
                                late = get_time_from_float(attendance.late)
                                if permission > 0.0:
                                    if permission >= late:
                                        permission -= late
                                        late = 0.0
                                    else:
                                        late -= permission
                                        permission = 0.0
                                if late > 0.0:
                                    if record.employee_id.attendance_id.rule_deduction_ids:
                                        for rule in record.employee_id.attendance_id.rule_deduction_ids.filtered(
                                                lambda r: r.type == 'late'):
                                            if rule.hour_level == '1':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if late >= time_from and late <= time_to:
                                                    if rule.id not in f_l_h_l:
                                                        f_l_h_l.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                            break
                                                    else:
                                                        if rule.id != int(first_hour_late[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break
                                                            else:
                                                                val_deduction += rule.deduction
                                                                break
                                            elif rule.hour_level == '2':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if late >= time_from and late <= time_to:
                                                    if rule.id not in s_l_h_l:
                                                        s_l_h_l.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                            break
                                                    else:
                                                        if rule.id != int(second_hour_late[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break
                                                            else:
                                                                val_deduction += rule.deduction
                                                                break
                                            elif rule.hour_level == '3':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if late >= time_from and late <= time_to:
                                                    if rule.id not in t_l_h_l:
                                                        t_l_h_l.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                    else:
                                                        if rule.id != int(third_hour_late[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break
                                                            else:
                                                                val_deduction += rule.deduction
                                                                break
                                            elif rule.hour_level == '4':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if late >= time_from and late <= time_to:
                                                    if rule.id not in fo_l_h_l:
                                                        fo_l_h_l.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                    else:
                                                        if rule.id != int(four_hour_late[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break

                                                            else:
                                                                val_deduction += rule.deduction
                                                                break
                                            elif rule.hour_level == '5':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if late >= time_from and late <= time_to:
                                                    if rule.id not in fi_l_h_l:
                                                        fi_l_h_l.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                    else:
                                                        if rule.id != int(second_hour_late[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break

                                                            else:
                                                                val_deduction += rule.deduction
                                                                break

                            if attendance.early > 0.0:
                                early = get_time_from_float(attendance.early)
                                if permission > 0.0:
                                    if permission >= early:
                                        permission -= early
                                        early = 0.0
                                    else:
                                        early -= permission
                                        permission = 0.0
                                if early > 0.0:
                                    if record.employee_id.attendance_id.rule_deduction_ids:
                                        for rule in record.employee_id.attendance_id.rule_deduction_ids.filtered(
                                                lambda r: r.type == 'early'):
                                            if rule.hour_level == '1':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if early >= time_from and early <= time_to:
                                                    if rule.id not in f_l_h_e:
                                                        f_l_h_e.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                            break
                                                    else:
                                                        if rule.id != int(first_hour_early[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break
                                                            else:
                                                                val_deduction += rule.deduction
                                                                break
                                            elif rule.hour_level == '2':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if early >= time_from and early <= time_to:
                                                    if rule.id not in s_l_h_e:
                                                        s_l_h_e.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                            break
                                                    elif s_l_h_e == second_hour_early:
                                                        if rule.id != int(second_hour_early[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break
                                                            else:
                                                                val_deduction += rule.deduction
                                                                break
                                            elif rule.hour_level == '3':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if early >= time_from and early <= time_to:
                                                    if rule.id not in t_l_h_e:
                                                        t_l_h_e.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                            break
                                                    else:
                                                        if rule.id != int(third_hour_late[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break
                                                            else:
                                                                val_deduction += rule.deduction
                                                                break
                                            elif rule.hour_level == '4':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if early >= time_from and early <= time_to:
                                                    if rule.id not in fo_l_h_e:
                                                        fo_l_h_e.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                            break
                                                    else:
                                                        if rule.id != int(four_hour_early[-1]):
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break
                                                            else:
                                                                val_deduction += rule.deduction
                                                                break
                                            elif rule.hour_level == '5':
                                                time_from = get_time_from_float(rule.time_from)
                                                time_to = get_time_from_float(rule.time_to)
                                                if early >= time_from and early <= time_to:
                                                    if rule.id not in fi_l_h_e:
                                                        fi_l_h_e.append(rule.id)
                                                        if rule.warning:
                                                            break
                                                        else:
                                                            val_deduction += rule.deduction
                                                            break
                                                    else:
                                                        if rule.id != five_hour_early[-1]:
                                                            continue
                                                        else:
                                                            if rule.warning:
                                                                break
                                                            else:
                                                                val_deduction += rule.deduction
                                                                break

                            if attendance.over_time > 0.0:
                                over_time = get_time_from_float(attendance.over_time)
                                if record.employee_id.attendance_id.rule_bonus_ids:
                                    for rule in record.employee_id.attendance_id.rule_bonus_ids:
                                        if attendance_datetime.strftime('%A') in weekend_days:
                                            if rule.rest_day:
                                                over_time_hour = over_time / 60
                                                overtime_hour += over_time_hour * rule.bonus_hours
                                                break
                                        else:
                                            time_from = get_time_from_float(rule.time_from)
                                            time_to = get_time_from_float(rule.time_to)
                                            if time_to >= over_time >= time_from:
                                                overtime_hour += rule.bonus_hours
                                                break

                else:
                    if single_date.strftime('%A') not in weekend_days:
                        check_date = str(single_date.date())
                        holidays = holidays_obj.search(
                            [('type', '=', 'remove'),('employee_id', '=', record.employee_id.id), ('state', 'in', ['validate', 'validate1']),
                             ('date_from', '<=', check_date), ('date_to', '>=', check_date)])
                        if holidays.filtered(lambda h: not h.holiday_status_id.is_permission):
                            pass
                        else:
                            if record.employee_id.attendance_id.rule_deduction_ids:
                                for rule in record.employee_id.attendance_id.rule_deduction_ids.filtered(
                                        lambda r: r.type == 'absent'):
                                    if rule.id not in absent_rule_take:
                                        if rule.absent_repeat == '1':
                                            absent_rule_take.append(rule.id)
                                            if rule.warning:
                                                break
                                            else:
                                                val_absence += rule.deduction
                                                break
                                        elif rule.absent_repeat == '2':
                                            absent_rule_take.append(rule.id)
                                            if rule.warning:
                                                break
                                            else:
                                                val_absence += rule.deduction
                                                break
                                        elif rule.absent_repeat == '3':
                                            absent_rule_take.append(rule.id)
                                            if rule.warning:
                                                break
                                            else:
                                                val_absence += rule.deduction
                                                break
                                        elif rule.absent_repeat == '4':
                                            absent_rule_take.append(rule.id)
                                            if rule.warning:
                                                break
                                            else:
                                                val_absence += rule.deduction
                                                break
                                        elif rule.absent_repeat == '5':
                                            absent_rule_take.append(rule.id)
                                            if rule.warning:
                                                break
                                            else:
                                                val_absence += rule.deduction
                                                break
                                    else:
                                        if rule.id != int(absent_rules[-1]):
                                            continue
                                        else:
                                            if rule.warning:
                                                break
                                            else:
                                                val_absence += rule.deduction
                                                break

            rrule = [

                {
                    'name': 'Overtime',
                    'code': 'Overtime',
                    'num_of_days': overtime_hour / hours,
                    'num_of_hours': overtime_hour,
                    'pay_amount': 0.0,
                    'rule_id': record.id,
                },

                {
                    'name': 'Deduction',
                    'code': 'Deduction',
                    'num_of_days': val_deduction / hours,
                    'num_of_hours': val_deduction,
                    'pay_amount': 0.0,
                    'rule_id': record.id,
                },
                {
                    'name': 'Absence',
                    'code': 'Absence',
                    'num_of_days': val_absence / hours,
                    'num_of_hours': val_absence,
                    'pay_amount': 0.0,
                    'rule_id': record.id,
                }
            ]

            for rr in rrule:
                record.write({'attend_rule_ids': [(0, 0, rr)]})

    @api.one
    @api.depends('attend_rule_ids')
    def _compute_deduction_amount(self):
        for record in self:
            amount = 0.0
            if record.attend_rule_ids:
                for line in record.attend_rule_ids.filtered(lambda r: r.code in ['Deduction']):
                    amount = line.num_of_days
            record.deduction_amount = amount

    @api.one
    @api.depends('attend_rule_ids')
    def _compute_overtime_amount(self):
        for record in self:
            if record.attend_rule_ids:
                for line in record.attend_rule_ids.filtered(lambda r: r.code == 'Overtime'):
                    record.overtime_amount = line.num_of_days

    @api.one
    @api.depends('attend_rule_ids')
    def _compute_absent_amount(self):
        for record in self:
            if record.attend_rule_ids:
                for line in record.attend_rule_ids.filtered(lambda r: r.code == 'Absence'):
                    record.absent_amount = line.num_of_days
