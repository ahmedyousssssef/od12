# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning


# ________________________________________________ Model

class hr_attendance_deduction(models.Model):
    _name = 'hr.attendance.deduction'
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True, )
    code = fields.Char(string="Code", required=False, )
    type = fields.Selection(string='Late/Early/Absent',
                            selection=[('late', 'Late Check In'), ('early', 'Early Check Out'), ('absent', 'Absent')],
                            required=True, )
    time_from = fields.Float(string='From')
    time_to = fields.Float(string='To')
    repetition = fields.Integer(string='Repetition')
    absent_repeat = fields.Selection(string="Repetition",
                                     selection=[('1', 'First Time'), ('2', 'Second Time'), ('3', 'Third Time'),
                                                ('4', 'Four Time'), ('5', 'Five Time'), ], required=False, )
    deduction = fields.Float(string='Deduction (Hours)')
    # absent = fields.Boolean(string='Absent')
    warning = fields.Boolean(string='Warning')
    hour_level = fields.Selection(string="Hour / Level",
                                  selection=[('1', 'First Hour'), ('2', 'Second Hour'), ('3', 'Third Hour'),
                                             ('4', 'Four Hour'), ('5', 'Five Hour')], required=False, )

    # _sql_constraints = [
    #     ('code_uniq', 'UNIQUE (code)', 'You can not have two rule with the same code !')
    # ]

    @api.one
    @api.depends('type', 'time_from', 'time_to', 'repetition', 'deduction', 'warning')
    def _compute_name(self):
        deduction = repetition = time_range = ''
        if self.type:
            type = dict([('late', 'Late Check In'), ('early', 'Early Check Out'), ('absent', 'Absent')])[self.type]
            if self.warning:
                deduction = ' [Warning]'
            elif self.deduction > 0:
                deduction = ' [' + str(self.deduction) + ('Hour]' if self.deduction <= 1 else 'Hours]')
            if self.repetition: repetition = ' [' + str(self.repetition) + (
                'Time]' if self.repetition <= 1 else 'Times]')
            if self.time_from or self.time_to:
                time = self.time_to - self.time_from
                uom = 'Hours]' if time > 2 else 'Hour]' if time >= 1 else 'Minutes]'
                time = "%02d:%02d" % (int(time), (time - int(time)) * 60)
                time_range = '[' + time + uom
            self.name = type + time_range + repetition + deduction
