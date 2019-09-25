# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PublicHoliday(models.Model):
    _name = 'hr.public.holiday'
    _rec_name = 'leave_type'
    _description = 'New Public Holiday'

    leave_type = fields.Many2one(comodel_name="hr.leave.type", string="Leave Type", required=True, )
    reason = fields.Char(string="Reason", required=False, )
    date_from = fields.Datetime(string="From", required=True, )
    date_to = fields.Datetime(string="To", required=True, )
    is_leave = fields.Boolean(string="Approved",default=False,)
    holiday_id = fields.Many2one(comodel_name="resource.calendar", string="Working Time", required=False, )

    # _sql_constraints = [
    #     ('date_check2', "CHECK ((date_from <= date_to))",
    #      "The start date must be anterior to the end date."),
    # ]

    @api.multi
    def create_leave(self):
        leave = self.env['hr.leave']
        employees = self.env['hr.employee'].search([('resource_calendar_id','=',self.holiday_id.id)])
        for employee in employees:
            line ={
                'employee_id':employee.id,
                'name':self.reason,
                'holiday_status_id':self.leave_type.id,
                'date_from':self.date_from,
                'date_to':self.date_to,
                'type':'remove',
            }
            emp_leave = leave.create(line)
            emp_leave._onchange_date_from()
            emp_leave.action_approve()
        self.is_leave = True





class HrHoliday(models.Model):
    _inherit = 'hr.leave.type'

    is_public = fields.Boolean(string="Is Public",  )



