from odoo import http
from odoo.http import request, route
from odoo.addons.portal.controllers import portal
from odoo import http, fields, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.addons.resource.models.utils import float_to_time, HOURS_PER_DAY
from odoo.osv.expression import AND
from operator import itemgetter
from collections import OrderedDict
import json
import base64
from datetime import datetime, time, date
from dateutil.relativedelta import relativedelta
from math import ceil
from pytz import timezone, UTC


class HRLeavesPortal(portal.CustomerPortal):

    def _to_utc(self, date, hour, resource):
        hour = float_to_time(float(hour))
        print(hour, "hour 26")
        holiday_tz = timezone(resource.tz or request.env.user.tz or 'UTC')
        return holiday_tz.localize(datetime.combine(date, hour)).astimezone(UTC).replace(tzinfo=None)
    
    @http.route(['/get/hour-per-day'], type='json', auth='user')
    def get_hours_per_day(self):
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        resource_calendar = employee_id.resource_calendar_id
        return resource_calendar.hours_per_day

    @http.route(['/get/leave-duration'], type='json', auth='user')
    def get_leave_duration(self, date_from, date_to, leave_type_request_unit, hour_from=None, hour_to=None, check_leave_type=True):
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        resource_calendar = employee_id.resource_calendar_id
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
        if not hour_from and not hour_to:
            date_to = date_to.replace(hour=23, minute=59, second=59)
        print(date_from, date_to, "date from date to 35\n\n")
        if leave_type_request_unit == 'hour' and hour_from is not None and hour_to is not None:
            print(hour_from, hour_to, "hour from hour to 34\n\n\n")
            print(date_from.date(), hour_from, employee_id, "date_from.date(), hour_from, employee_id 40\n\n\n")
            date_from = self._to_utc(date_from.date(), hour_from, employee_id)
            date_to = self._to_utc(date_to.date(), hour_to, employee_id)
        print(date_from, date_to, "date from date to 39\n\n")
        domain = [('time_type', '=', 'leave'),
                      ('company_id', 'in', request.env.companies.ids + request.env.context.get('allowed_company_ids', [])),
                      # When searching for resource leave intervals, we exclude the one that
                      # is related to the leave we're currently trying to compute for.
                      '|', ('holiday_id', '=', False)]
        work_time_per_day_mapped = employee_id._list_work_time_per_day(date_from, date_to, calendar=resource_calendar, domain=domain)
        work_days_data_mapped = employee_id._get_work_days_data_batch(date_from, date_to, calendar=resource_calendar, domain=domain)
        print(work_time_per_day_mapped, "work_time_per_day_mapped 57")
        print(work_days_data_mapped, "work_days_data_mapped 58")

        if not date_from or not date_to or not resource_calendar:
            return (0, 0)
        hours, days = (0, 0)
        if employee_id:


            if leave_type_request_unit == 'day' and check_leave_type:
                print(employee_id.id, "employee_id.id 83")
                work_time_per_day_list = work_time_per_day_mapped[employee_id.id]
                days = len(work_time_per_day_list)
                hours = sum(map(lambda t: t[1], work_time_per_day_list))
            else:
                work_days_data = work_days_data_mapped[employee_id.id]
                hours, days = work_days_data['hours'], work_days_data['days']
        else:
            today_hours = resource_calendar.get_work_hours_count(
                datetime.combine(date_from.date(), time.min),
                datetime.combine(date_from.date(), time.max),
                False)
            hours = resource_calendar.get_work_hours_count(date_from, date_to)
            days = hours / (today_hours or HOURS_PER_DAY)
        if leave_type_request_unit == 'day' and check_leave_type:
            days = ceil(days)
        return (days, hours)

    @http.route(['/fetch/hr_leave'],type='json', auth='user')
    def fetch_hrleave(self, param1):
        leave = request.env['hr.leave'].sudo().search_read([('id', '=', int(param1))])
        print(leave, "leave id \n\n\n\n")
        return leave

    @http.route(['/remove/timeoff'],type='http', auth="user",methods=['POST'], csrf=False, website=True)
    def remove_leave(self, **post):
        leave_id = request.env['hr.leave'].sudo().browse([int(post.get('leave_id'))])
        if leave_id:
            leave_id._force_cancel(post.get('notes'), 'mail.mt_note')
        return request.redirect('/my/timeoff')


    @http.route('/check/attachment', type='json', auth='user')
    def check_attachment(self, param1):
        # Process the request and return a response
        is_allocation_attach = False
        if param1:
            allocation = request.env['hr.leave.type'].sudo().browse([int(param1)])
            if allocation:
                if allocation.support_document:
                    is_allocation_attach= True
        return is_allocation_attach

    @route(['/my/leaves'], type='http', auth="user", website=True)
    def my_leaves(self, sortby='date', filterby='all', **kw):
        leave_types = request.env['hr.leave.type'].sudo().search([('requires_allocation', '=', 'yes'),('employee_requests', '=', 'yes')])
        print(leave_types, "leave types\n\n\n\n\n\n\n\n\n\n\n")
        leaves = request.env['hr.leave.allocation'].sudo().search([])
        my_leaves = leaves.filtered(lambda a: a.employee_id.user_id.id == request.env.user.id)
        values = { 
            "page_name": "leaves",
            "leave_types": leave_types,
        }
        if my_leaves:
            print(my_leaves, "my leaves 49\n\n\n")
            holidays = my_leaves[0].with_context(
            default_company_id=request.env.company.id,
            from_dashboard=True,
            allowed_company_ids=[request.env.company.id]).holiday_status_id.get_allocation_data_request()

            for holiday in holidays:
                data = list(holiday)
                # print(data, "\n\ndata\n")
                data[1]["requires_allocation"] = bool(data[2] == 'yes')
                data[1]["name"] = data[0]
                data[1]["lang"] = request.env.user.lang
                print(data, "\n\n")
                holiday = tuple(data)
            # print(holidays, "holidays\n\n\n")
            print(len(holidays), "holidays\n\n\n")
            for leave in my_leaves:
                print(leave.name, "name\n")
                print(leave.number_of_days, "num of days\n")
                print(leave.leaves_taken, "num of days taken \n")
                print(leave.holiday_status_id.virtual_remaining_leaves, "remaining \n")
            allocation = request.env['hr.leave.allocation'].sudo().search([])
            allocation_ids = allocation.filtered(lambda a: a.employee_id.user_id.id == request.env.user.id)
            allow_timeoff = False
            for leave in my_leaves:
                if leave.state == 'validate' and ((leave.holiday_status_id.virtual_remaining_leaves and leave.holiday_status_id.virtual_remaining_leaves > 0) or leave.number_of_days > 0):
                    allow_timeoff = True
                    break
            values = {
                "leaves": my_leaves,
                "allocations":allocation_ids,
                "page_name": "leaves",
                "allow_timeoff": allow_timeoff,
                "leave_types": leave_types,
                "holidays": holidays,
                "holidays_length": len(holidays)
            }
            for i in values["holidays"]:
                print(i, "\n")
        return request.render('sttl_portal_leaves.my_leaves', values)
    

    def _leave_get_portal_domain(self):
        return [('employee_id.user_id.id', '=', request.env.user.id), ('state', '!=', 'cancel')]

    def get_groupby_mapping(self):
        return {
            'holiday_status_id': 'holiday_status_id',
        }

    def _get_my_leaves_searchbar_sortings(self):
        return {
            'date': {'label': _('Date'), 'order': 'date_from desc'},
            'state': {'label': _('Status'), 'order': 'state desc'},
        }

    def get_searchbar_groupby(self):
        return {
            'none': {'input': 'none', 'label': _('None')},
            'holiday_status_id': {'input': 'holiday_status_id', 'label': _('Time Off Type')}
        }

    @route(['/my/timeoff', '/my/timeoff/page/<int:page>'], type='http',csrf=False, auth="user", website=True)
    def my_timeoff(self, page=1, sortby='date', groupby='none', filterby='all', search=None, search_in='all', url="/my/timeoff", **kw):
        print(kw, "\n\n\nkw")
        print(request.env.user, "\n\n\n")
        print("Fetching cancelled leaves=====================209")
        allocation = request.env['hr.leave.allocation'].sudo().search([])
        allocation_ids = allocation.filtered(lambda a: a.employee_id.user_id.id == request.env.user.id and a.state == 'validate' and 
        ((a.holiday_status_id.virtual_remaining_leaves and a.holiday_status_id.virtual_remaining_leaves > 0)
        or (a.holiday_status_id.allows_negative and a.holiday_status_id.max_allowed_negative and a.holiday_status_id.virtual_remaining_leaves > -a.holiday_status_id.max_allowed_negative )))
        print(allocation_ids, "allocation ids\n\n\n")

        allocations = []
        for alloc in allocation_ids:
            if alloc.holiday_status_id not in allocations:
                allocations.append(alloc.holiday_status_id)
        start_date = date.today().strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        timeoff_types = request.env['hr.leave.type'].sudo().search([])
        print(allocations, "allocations 91")
        for timeoff_type in timeoff_types:
            if timeoff_type not in allocations and timeoff_type.requires_allocation == 'no':
                allocations.append(timeoff_type)
        print(allocations, "allocations\n\n\n\n\n\n\n\n\n")

        _items_per_page = 100
        Leave = request.env['hr.leave']
        domain = self._leave_get_portal_domain()
        Leave_sudo = Leave.sudo()
        searchbar_sortings = self._get_my_leaves_searchbar_sortings()
        searchbar_groupby = self.get_searchbar_groupby()

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date_from", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('date_from', '>=', date_utils.start_of(today, "week")), ('date_from', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date_from', '>=', date_utils.start_of(today, 'month')), ('date_from', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date_from', '>=', date_utils.start_of(today, 'year')), ('date_from', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('date_from', '>=', quarter_start), ('date_from', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date_from', '>=', date_utils.start_of(last_week, "week")), ('date_from', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('date_from', '>=', date_utils.start_of(last_month, 'month')), ('date_from', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date_from', '>=', date_utils.start_of(last_year, 'year')), ('date_from', '<=', date_utils.end_of(last_year, 'year'))]},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])
        leave_count = Leave_sudo.search_count(domain)

        pager = portal_pager(
            url="/my/timeoff",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby, 'groupby': groupby},
            total=leave_count,
            page=page,
            step=_items_per_page
        )

        def get_leaves():
            groupby_mapping = self.get_groupby_mapping()
            field = groupby_mapping.get(groupby, None)
            print(groupby_mapping, "groupby_mapping 177")
            print(groupby, "group by 177")
            print(field, "field\n\n")
            orderby = '%s, %s' % (field, order) if field else order
            leaves = Leave_sudo.search(domain, order=orderby, limit=_items_per_page, offset=pager['offset'])
            if field:
                if groupby == 'date':
                    raw_timesheets_group = Leave_sudo._read_group(
                        domain, ['date:day'], ['number_of_days:sum', 'id:recordset']
                    )
                    groupped_leaves = [(records, unit_amount) for __, unit_amount, records in raw_timesheets_group]

                else:
                    time_data = Leave_sudo._read_group(domain, [field], ['number_of_days:sum'])
                    mapped_time = {field.id: unit_amount for field, unit_amount in time_data}
                    groupped_leaves = [(Leave_sudo.concat(*g), mapped_time[k.id]) for k, g in groupbyelem(leaves, itemgetter(field))]
                return leaves, groupped_leaves
            print(domain, "domain 169\n\n\n")
            groupped_leaves = [(
                leaves,
                sum(Leave_sudo.search(domain).mapped('number_of_days'))
            )] if leaves else []
            return leaves, groupped_leaves

        leaves, grouped_leaves = get_leaves()
        print(groupby, "groupby\n\n\n\n\n")
        
        values = {
            "leaves": leaves,
            'grouped_leaves': grouped_leaves,
            "allocations":allocations,
            "start_date":start_date,
            "end_date":end_date,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'filterby': filterby,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'groupby': groupby,
            "duration":"1",
            'default_url': url,
            "page_name": "timeoff",
            "allow_timeoff": kw.get('allow_timeoff'),
        }
        return request.render('sttl_portal_leaves.my_timeoff', values)

    @http.route(['/add/timeoff'], type='http', auth="user", methods=['POST'], csrf=False, website=False)
    def add_timeoff(self, **kw):
        print(kw, "kw 239")
        date_from, date_to = kw.get('date_from'), kw.get('date_to')
        files = request.httprequest.files.getlist('files')
        print(files, "Files received")
        employee_user = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        date_from_object = datetime.strptime(date_from, "%Y-%m-%d").date()
        if date_to:
            date_to_object = datetime.strptime(date_to, "%Y-%m-%d").date()
        else:
            date_to_object = date_from_object
        if date_to_object < date_from_object:
            response = {
                'status': 'warning',
                'error': "Leave end date cannot be less than Leave start date"
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=400
            )
        if date_from and date_to:
            print(date_from, date_to, "date from date to\n\n\n")
            mandatory_days = employee_user._get_mandatory_days(
                date_from,
                date_to
            )
            if mandatory_days:
                response = {
                    'status': 'warning',
                    'error': "You are not allowed to request a Time Off on a Mandatory Day."
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )
        print(kw.get("edit"), type(kw.get("edit")), "edit\n\n\n\n\n")
        if kw.get("edit"):
            all_leaves = request.env['hr.leave'].sudo().search([
                ('id', '!=', kw.get('id')),
                ('employee_id', '=', employee_user.id),
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from),
                ('state', 'not in', ['cancel', 'refuse']),
            ])
        else:
            all_leaves = request.env['hr.leave'].sudo().search([
                ('employee_id', '=', employee_user.id),
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from),
                ('state', 'not in', ['cancel', 'refuse']),
            ])
        print(all_leaves, "all_leaves\n\n\n")
        if all_leaves:
            response = {
                'status': 'warning',
                'error': "You've already booked Time Off which overlaps with this period"
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=400
            )
        
        all_allocations = request.env['hr.leave.allocation'].sudo().search([
            ('holiday_status_id', '=', int(kw.get('holiday_status_id'))),
            ('employee_id', '=', employee_user.id),
            ('state', 'not in', ['confirm', 'refuse']),
        ])
        alloc_length = 0
        
        for allocation in all_allocations:
            print(allocation, "allocation\n\n\n")
            if allocation.date_from:
                if allocation.date_from > date_from_object or allocation.date_from > date_to_object:
                    alloc_length += 1
            if allocation.date_to:
                if allocation.date_to < date_from_object or allocation.date_to < date_to_object:
                    alloc_length += 1
            if allocation.holiday_status_id.allows_negative and allocation.holiday_status_id.max_allowed_negative and not kw.get('edit'):
                if allocation.holiday_status_id.virtual_remaining_leaves <= -allocation.holiday_status_id.max_allowed_negative:
                    print(allocation.holiday_status_id.virtual_remaining_leaves, "remaining leaves")
                    print(allocation.holiday_status_id.max_allowed_negative, "max negative\n")
                    print(-allocation.holiday_status_id.max_allowed_negative, -allocation.holiday_status_id.max_allowed_negative < 0)
                    print("Max negative reached\n\n\n")
                    response = {
                    'status': 'warning',
                    'error': "There is no valid allocation to cover that request."
                    }
                    return request.make_response(
                        json.dumps(response),
                        headers=[('Content-Type', 'application/json')],
                        status=400
                    )
        if alloc_length >= len(all_allocations) and len(all_allocations) > 0:
            print("\n\n\n\n\nInvalid leave\n\n\n\n\n")
        
            
            response = {
                    'status': 'warning',
                    'error': "There is no valid allocation to cover that request."
                }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=400
            )
        
        leave_vals = {
            'name': kw.get('name'),
            'employee_id': employee_user.id,
            'holiday_status_id': int(kw.get('holiday_status_id')),
            'request_date_from': date_from,
            'request_date_to': date_to,
            'request_hour_from': kw.get('request_hour_from'),
            'request_hour_to': kw.get('request_hour_to'),
            'date_from': date_from,
            'date_to': date_to,
            'state': 'confirm',  
            'request_unit_half': True if kw.get('request_unit_half') == 'half_day' else False,
            'request_unit_hours': True if kw.get('request_unit_half') == 'custom_hours' else False,
        }
        total_days = float(kw.get('total_days').split(' ')[0])
        print(total_days, "total days 407\n\n\n")
        leave_type = request.env['hr.leave.type'].sudo().browse([int(kw.get('holiday_status_id'))])
        print(leave_type.virtual_remaining_leaves, "leave_type.virtual_remaining_leaves 434\n\n")
        print(leave_type.virtual_remaining_leaves - total_days, "difference between days 435\n\n\n")

        date_change = False
        if kw.get("edit"):
            leave_id = kw.get('id')
            leave_record = request.env['hr.leave'].sudo().search([('id', '=', leave_id)])
            print(date_from, date_to, leave_record.request_date_from, leave_record.request_date_to, "existing date from and date to 439\n\n")
            if leave_record.request_date_from != date_from_object or leave_record.request_date_to != date_to_object:
                date_change = True

        if leave_type.allows_negative and date_change == False and not kw.get("edit"):
            print("not date change and negative 444\n\n")
            for employee in employee_user:
                if leave_type and (leave_type.virtual_remaining_leaves - total_days) < -leave_type.max_allowed_negative:
                    response = {
                    'status': 'warning',
                    'error': "There is no valid allocation to cover that request."
                    }
                    return request.make_response(
                        json.dumps(response),
                        headers=[('Content-Type', 'application/json')],
                        status=400
                    )
        elif not leave_type.allows_negative and date_change == False and not kw.get("edit"):
            print("no date change and no negative 458\n\n")
            if leave_type.requires_allocation == 'yes':
                for employee in employee_user:
                    if leave_type and (leave_type.virtual_remaining_leaves - total_days) < 0:
                        response = {
                        'status': 'warning',
                        'error': "There is no valid allocation to cover that request."
                        }
                        return request.make_response(
                            json.dumps(response),
                            headers=[('Content-Type', 'application/json')],
                            status=400
                        )
        elif not leave_type.allows_negative and date_change == True:
            print("date change and no negative 468\n\n")
            if leave_record.holiday_status_id.request_unit == 'day' and leave_type.requires_allocation == 'yes':
                if total_days > leave_record.number_of_days:
                    total_days = total_days - leave_record.number_of_days 
                    for employee in employee_user:
                        if leave_type and (leave_type.virtual_remaining_leaves - total_days) < 0:
                            response = {
                            'status': 'warning',
                            'error': "There is no valid allocation to cover that request."
                            }
                            return request.make_response(
                                json.dumps(response),
                                headers=[('Content-Type', 'application/json')],
                                status=400
                            )

        elif leave_type.allows_negative and date_change == True:
            print("date change and  negative 488\n\n",leave_record.number_of_days)
            if leave_record.holiday_status_id.request_unit == 'day':
                if total_days > leave_record.number_of_days:
                    total_days = total_days - leave_record.number_of_days
                    print(total_days,leave_type.max_allowed_negative, "total_days leave_type.max_allowed_negative 493\n")
                    for employee in employee_user:
                        if leave_type and (leave_type.virtual_remaining_leaves - total_days) < -leave_type.max_allowed_negative:
                            response = {
                            'status': 'warning',
                            'error': "There is no valid allocation to cover that request."
                            }
                            return request.make_response(
                                json.dumps(response),
                                headers=[('Content-Type', 'application/json')],
                                status=400
                            )

        leave_vals = {k: v for k, v in leave_vals.items() if v or v is False}
        if leave_vals['request_unit_half'] or leave_vals['request_unit_hours']:
            leave_vals['request_date_to'] = date_from
        try:
            leave_record = ""
            if kw.get("edit"):
                leave_id = kw.get('id')
                if kw.get('files'):
                    del kw['files']
                if kw.get('total_days'):
                    del kw['total_days']
                del kw["edit"]
                del kw["id"]
                kw['holiday_status_id'] = int(kw['holiday_status_id'])
                print(kw, "kw before edit 360\n\n\n")
                leave_record = request.env['hr.leave'].sudo().search([('id', '=', leave_id)])
                print(leave_record, "leave record 482\n\n")
                if leave_record:
                    leave_record.write(kw)
                    if files:
                        attachment_ids = []
                        for file in files:
                            # Create an attachment
                            attachment = request.env['ir.attachment'].sudo().create({
                                'name': file.filename,
                                'type': 'binary',
                                'datas': base64.b64encode(file.read()),
                                'res_model': 'hr.leave',
                                'res_id': leave_record.id,
                            })
                            attachment_ids.append(attachment.id)
                        leave_record.write({
                            'supported_attachment_ids' : [(4, attachment_id) for attachment_id in attachment_ids]
                        })
                    print("\n\n\nRecord edited successfully\n\n\n")
                    return request.make_response(
                        json.dumps({'status': 'success', 'message': 'Time off request edited successfully'}),
                        headers=[('Content-Type', 'application/json')], status=200
                    )
            else:
                print("creating leave 547\n\n\n")
                leave_record = request.env['hr.leave'].sudo().with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True,
                    no_calendar_sync=True,
                    leave_skip_state_check=True,
                    leave_compute_date_from_to=True,
                ).create(leave_vals)
                print(leave_record, "leave_record after create\n\n\n")
                if leave_record:
                    if files:
                        attachment_ids = []
                        for file in files:
                            # Create an attachment
                            attachment = request.env['ir.attachment'].sudo().create({
                                'name': file.filename,
                                'type': 'binary',
                                'datas': base64.b64encode(file.read()),
                                'res_model': 'hr.leave',
                                'res_id': leave_record.id,
                            })
                            attachment_ids.append(attachment.id)
                        leave_record.write({
                            'supported_attachment_ids' : [(4, attachment_id) for attachment_id in attachment_ids]
                        })
                    print(leave_record, "leave\n\n\n")
                    return request.make_response(
                        json.dumps({'status': 'success', 'message': 'Time off request added successfully'}),
                        headers=[('Content-Type', 'application/json')], status=200
                    )
                    
        except Exception as e:
            print("434",leave_record, not kw.get("edit"))
            print(type(e), "type exception\n\n\n\n")
            print(str(e).lower(), "exception\n\n\n\n")

            response = {
                'status': 'warning',
                'error': str(e)
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=400
            )
        except Warning as w:
            response = {
                'status': 'warning',
                'error': str(w)
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    @route(['/add/allocation'], type='http', auth="user", csrf=False, website=True)
    def add_allocation(self,  sortby='date', filterby='all', **kw):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        print(employee.id, employee.name, "name")
        kw["employee_id"] = employee.id
        print(kw, "\n\n\nkw\n")
        allocation = request.env['hr.leave.allocation'].sudo().create(kw)
        print(allocation, "allocation\n\n")
        if allocation:
            return request.redirect('/my/leaves')


class LeavesPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        employee_user = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        print(employee_user, "employee\n\n\n")
        print(request.env.user.share, "share\n\n\n")
        if employee_user:
            if request.env.user.share == True: 
                values['em_user'] = True
            else:
                values['em_user'] = False
        else:
             values['em_user'] = False
        return values
