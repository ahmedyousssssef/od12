# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning


#________________________________________________ Model

class hr_attendance_bonus(models.Model):
    _name = 'hr.attendance.bonus'
    _rec_name = 'name'

    name = fields.Char(string='Name',compute='_compute_name', store=True, readonly=True, )
    # bonus_type = fields.Selection(string='Bonus Type', selection=[('hour', 'Hour Bonus'), ('fixed', 'Fixed Bonus')],
    #                               default='hour', readonly=False, )
    time_from = fields.Float(string='From')
    time_to = fields.Float(string='To')
    # start = fields.Float(string='Start')
    bonus_hours = fields.Float(string='Bonus (Hours)')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id.id, )
    # bonus_fixed = fields.Monetary(string='Bonus', currency_field='currency_id', )
    rest_day = fields.Boolean(string='Rest Day')



    @api.one
    @api.depends('time_from','time_to','bonus_hours','rest_day')
    def _compute_name(self):
        if self.rest_day:
            self.name = '[' + str(self.bonus_hours) + 'Hours] Rest Day'
        else:
            self.name = '[' + str(self.bonus_hours) + 'Hours]'
