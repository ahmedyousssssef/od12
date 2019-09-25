# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning

class HrAttendanceRule(models.Model):
    _name = 'hr.attendance.structure'
    _rec_name = 'name'

    name = fields.Char(string="Name", required=False, )
    code = fields.Char(string="Code", required=False, )
    permission = fields.Float(string="Permission Minutes",  required=False, )
    bonus_type = fields.Selection(string='Bonus Type', selection=[('hour', 'Hour Bonus'), ('fixed', 'Fixed Bonus')],
                                  default='hour',)
    rule_bonus_ids = fields.Many2many(comodel_name="hr.attendance.bonus", string="Bonus Rules", required=False, )
    rule_deduction_ids = fields.Many2many(comodel_name="hr.attendance.deduction", string="Deduction Rules", required=False, )

    # @api.onchange('rule_bonus_ids')
    # def onchange_rule_bonus_ids(self):
    #     if len(self.rule_bonus_ids) > 1:
    #         raise Warning(_("You Could not add More Bouns Rules , only one"))


