import logging
import math

from datetime import datetime
from pytz import timezone, UTC

from odoo import api, fields, models
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class HolidaysRequest_innnherit(models.Model):
    _inherit = "hr.leave"

    def _default_get_request_parameters(self, values):
        new_values = dict(values)
        global_from, global_to = False, False
        # TDE FIXME: consider a mapping on several days that is not the standard
        # calendar widget 7-19 in user's TZ is some custom input
        if values.get('date_from'):
            user_tz = self.env.user.tz or 'UTC'
            #################################################################### edit
            date2_from = datetime.strptime(str(values['date_from']), "%Y-%m-%d")
            localized_dt = timezone('UTC').localize(date2_from).astimezone(timezone(user_tz))
            #################################################################### end edit
            global_from = localized_dt.time().hour == 7 and localized_dt.time().minute == 0
            #################################################################### edit
            new_values['request_date_from'] = values['date_from']
            #################################################################### end edit
        if values.get('date_to'):
            user_tz = self.env.user.tz or 'UTC'
            #################################################################### edit
            date2_to = datetime.strptime(str(values['date_to']), "%Y-%m-%d")
            localized_dt = timezone('UTC').localize(date2_to).astimezone(timezone(user_tz))
            #################################################################### end edit
            global_to = localized_dt.time().hour == 19 and localized_dt.time().minute == 0
            #################################################################### edit
            new_values['request_date_to'] = values['date_to']
            #################################################################### end edit
        if global_from and global_to:
            new_values['request_unit_custom'] = True
        return new_values

    @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
                  'request_date_from', 'request_date_to',
                  'employee_id')
    def _onchange_request_parameters(self):
        if not self.request_date_from:
            self.date_from = False
            return

        if self.request_unit_half or self.request_unit_hours:
            self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return

        domain = [('calendar_id', '=',
                   self.employee_id.resource_calendar_id.id or self.env.user.company_id.resource_calendar_id.id)]
        attendances = self.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

        # find first attendance coming after first_day
        attendance_from = next((att for att in attendances if int(att.dayofweek) >= self.request_date_from.weekday()),
                               attendances[0])
        # find last attendance coming before last_day
        attendance_to = next(
            (att for att in reversed(attendances) if int(att.dayofweek) <= self.request_date_to.weekday()),
            attendances[-1])

        if self.request_unit_half:
            if self.request_date_from_period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
        elif self.request_unit_hours:
            hour_from = float_to_time(self.request_hour_from)
            hour_to = float_to_time(self.request_hour_to)
        elif self.request_unit_custom:
            hour_from = self.date_from.time()
            hour_to = self.date_to.time()
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)

        tz = self.env.user.tz if self.env.user.tz and not self.request_unit_custom else 'UTC'  # custom -> already in UTC
        #################################################################### edit
        datefrom = timezone(tz).localize(
            datetime.combine(fields.Date.from_string(self.request_date_from), hour_from)).astimezone(UTC).replace(
            tzinfo=None)
        date_to = timezone(tz).localize(
            datetime.combine(fields.Date.from_string(self.request_date_to), hour_to)).astimezone(UTC).replace(
            tzinfo=None)
        self.date_from = datefrom.date()
        # print ("datefrom")
        self.date_to = date_to.date()
        # print ("date_to")
        #################################################################### end edit
