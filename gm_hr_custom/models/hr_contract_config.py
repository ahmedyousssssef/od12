# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrConfigSettings(models.TransientModel):
    _name = 'hr.config.settings'
    _inherit = 'res.config.settings'

    trail_days = fields.Integer(string="Days To Start Contract",  required=False, )
    renew_days = fields.Integer(string="Days To Renew Contract",  required=False, )
