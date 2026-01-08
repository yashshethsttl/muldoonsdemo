/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.PortalTimeoffModal  = publicWidget.Widget.extend({
    selector: '#timeoffModal',
    events: {
        'change .leave_dates': 'count_duration',
        'change #time-off-type': 'check_request_unit',
        'click .hour_check': 'onlyOne',
        'change .hour_select': 'count_hours_duration',
        'submit #timeoff-form': 'add_timeoff',
    },

    start : async function(){
        this.request_unit = '';
        this.templates = await rpc('/get/templates')
        console.log(this.templates, "templates 21")
    },

    check_until: function(event){
        let changedElement = event.currentTarget;
        console.log(changedElement.value, "changed element")
    },

    count_duration: async function() {
        let start_time = document.getElementById('start-time')
        let end_time = document.getElementById('end-time')
        let timeoff_error = document.getElementById("timeoff-error")
        timeoff_error.innerHTML = "";
        let from = document.getElementById("start-date")
        let to = document.getElementById("end-date")
        if(start_time && end_time){
            to.value = from.value
        }
        let from_date = new Date(from.value)
        let to_date = new Date(to.value)
        console.log(to_date, from_date, "to date from date 37")
        let hours_checkboxes = document.getElementsByName("request_unit_half")
        console.log(hours_checkboxes, "hour checkbox")
        console.log(from, to, "from to")
        if (from.value && (to.value || (start_time && end_time))) {
            if(this.request_unit == 'day'){
                let duration = await rpc('/get/leave-duration', {'date_from': from.value, 'date_to': to.value, 'leave_type_request_unit': this.request_unit})
                console.log(duration, "duration <<<<<<<<< 45")
                document.getElementById('leave_duration').value = duration[0] + " Days"
            }
            else{
                if(start_time && end_time){
                    var duration = await rpc('/get/leave-duration', {'date_from': from.value, 'date_to': to.value,
                        'hour_from': start_time.value, 'hour_to': end_time.value, 'leave_type_request_unit': this.request_unit})
                    console.log(duration, "duration 62")
                    document.getElementById('leave_duration').value = duration[1] + " Hours"
                    return
                }
                else{
                    var duration = await rpc('/get/leave-duration', {'date_from': from.value, 'date_to': to.value, 'leave_type_request_unit': this.request_unit})
                console.log(duration, "duration <<<<<<<<< 45")
                }
                document.getElementById('leave_duration').value = duration[0] + " Days (" + duration[1] + " Hours)"
            }
        }
    },

    check_request_unit: async function() {
        console.log(this, "this");
        let selectedTimeoff = document.getElementById("time-off-type").value;
        
        if(selectedTimeoff != ""){
            console.log(selectedTimeoff);
            let response = await $.ajax({
                url: "/get/timeoff_type",
                method: "GET",
                dataType: 'json',
                data: { id: selectedTimeoff }
            });
            console.log(response, "response");
            this.request_unit = response.request_unit;
            const timeoffContainer = document.getElementById('timeoff-selection')
            const duration_div = document.getElementById('duration')
            timeoffContainer.style.display = 'block';
            if (response.request_unit == 'hour') {
                console.log("hours");
                
                timeoffContainer.innerHTML = this.templates.request_unit_hour
                duration_div.innerHTML = this.templates.leave_duration
               
            }
            else {
                timeoffContainer.innerHTML = this.templates.request_unit_days
                duration_div.innerHTML = this.templates.leave_duration
               
            }
        }
        else{
            const timeoffContainer = document.getElementById('timeoff-selection')
            const duration_div = document.getElementById('duration')
            timeoffContainer.style.display = 'none';
            timeoffContainer.innerHTML = ""
            duration_div.innerHTML = ""
        }
    },

    onlyOne: function(event) {
        var changedElement = event.currentTarget; 
        console.log(changedElement, "changedElement 105");
    
        var checkboxes = document.getElementsByName("request_unit_half");
    
        Array.from(checkboxes).forEach((item) => {
            if (item !== changedElement) {
                item.checked = false;
            }
        });
    
        this.hours_change(changedElement);
    },
    

    hours_change: async function(currentValue) {
        console.log(currentValue.value, "current value");
        const leave_duration = document.getElementById('leave_duration');
        let start_date_label = document.getElementById('start-date-label');
        const timeoffContainer = document.getElementById('hour-selection');
        let duration_period = document.getElementById('request_date_from_period')
        let end_date = document.getElementById('end-date-div')
        let end_date_input  = document.getElementById("end-date")
        timeoffContainer.style.display = 'block';
        if (currentValue.value == 'half_day' && currentValue.checked == true) {
            let half_day_duration = await rpc('/get/hour-per-day') / 2


            leave_duration.value = half_day_duration + " Hours"
            
            end_date.value = ""
            end_date.style.display = "none";
            
            end_date_input.required = false;
            duration_period.value = 'am'
            let period = document.getElementById('request_date_from_period')
            period.style.display = "block";
            timeoffContainer.innerHTML = ``;
            start_date_label.innerHTML = "Date"
        }
        else if (currentValue.value == 'custom_hours' && currentValue.checked == true) {
            end_date.value = ""
            end_date.style.display = "none";
            end_date_input.required = false;
            duration_period.value = ''
            duration_period.style.display = 'none'
            duration_period.required = false;
            leave_duration.value = ""
            timeoffContainer.innerHTML = this.templates.time_selection
    
        }
        else {
            console.log("else 226")
            end_date.style.display = 'block';
            end_date_input.required = true;
            duration_period.value = ''
            duration_period.style.display = 'none'
            duration_period.required = false;
            timeoffContainer.innerHTML = ""
            leave_duration.value = ""
            this.count_duration()
        }
    },

    count_hours_duration: function(){
        let start_time = document.getElementById('start-time').value
        let end_time = document.getElementById('end-time').value
        console.log(start_time, "start_time")
        console.log(end_time, "end_time")
        if(start_time && end_time > 0){
            console.log("calling count duration method 197 ")
            this.count_duration()
        }
            
    },

    add_timeoff: function(e){
        e.preventDefault();
    
        const formElements = [
            document.getElementById("time-off-type"),
            document.getElementById("start-date"),
            document.getElementById("request_date_from_period"),
            document.getElementById("end-date"),
            document.getElementById("message-text"),
            document.getElementById("start-time"),
            document.getElementById("end-time"),
        ];
        let files_input = document.getElementById("myfile");
        
        const hourlyLeaveType = document.querySelector("input[name='request_unit_half']:checked");
    
        let formData = new FormData();
    
        formElements.forEach(element => {
            if (element && element.value !== "") {
                formData.append(element.name, element.value);
            }
        });
    
        if (hourlyLeaveType) {
            formData.append(hourlyLeaveType.name, hourlyLeaveType.value);
        }
    
        for (let i = 0; i < files_input.files.length; i++) {
            formData.append('files', files_input.files[i]);
        }
    
        let unit_half = document.getElementsByName("request_unit_half")
        unit_half.forEach(element => {
            if(element.checked){
                formData.append(element.name, element.value);
            }
        });
        let leave_duration = document.getElementById('leave_duration').value
        formData.append("total_days", leave_duration);
    
        console.log("Form submit");
        console.log(formData);
        
        fetch('/add/timeoff', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log(response); 
            if (response.status === 400) {
                return response.json().then(errorResponse => {
                    console.log(errorResponse, "errorResponse");
                    if(errorResponse.status == "warning"){
                        document.getElementById("timeoff-error").innerHTML = errorResponse.error;
                    }
                });
            }
            else if(response.status === 200){
                location.reload()
            }
            return response.json(); 
        })
        .catch(error => console.error('Error:', error));
    }
    

})


publicWidget.registry.PortalTimeoffAllocation = publicWidget.Widget.extend({
    selector: '#LeaveAllocationModal',
    events: {
        'change #time-off-type-allocation': 'check_request_unit',
    },

    check_request_unit: async function() {
        console.log(this, "this");
        let selectedTimeoff = document.getElementById("time-off-type-allocation").value;
        console.log(selectedTimeoff, "selectedtimeoff 373")
        if(selectedTimeoff != ""){
            console.log(selectedTimeoff);
            let response = await $.ajax({
                url: "/get/timeoff_type",
                method: "GET",
                dataType: 'json',
                data: { id: selectedTimeoff }
            });
            console.log(response, "response");
            if (response.request_unit == 'hour') {
                document.getElementById("amount_unit").innerHTML = 'Hours'
            }
            else{
                document.getElementById("amount_unit").innerHTML = 'Days'
            }
        }
        else{
            document.getElementById("amount_unit").innerHTML = 'Days'
        }
    }
    
})


publicWidget.registry.PortalTimeoff = publicWidget.Widget.extend({
    selector: '#timeoff-div',
    events: {
        
    },

    start: function () {
        var self = this;
        $('#CancelLeaveModal').on('show.bs.modal', function (event) {
            self.loadCancelTimeoff(event);
        });
        return this._super.apply(this, arguments);
    },

    loadCancelTimeoff: function(event){
        console.log("load cancel timeoff");
        const button = event.relatedTarget;
        const leaveId = button.getAttribute('data-leave-id');
        const modalLeaveId = document.querySelector('#modal-leave-id');
        if(modalLeaveId){
            modalLeaveId.value = leaveId;  
        }
    },
});


publicWidget.registry.PortalTimeoffEditModal  = publicWidget.Widget.extend({
    selector: '#EditLeaveModal',
    events: {
        'change .leave_dates': 'count_duration',
        'click .edit_attachment': '_onClickEdit',
        'change #time-off-type-edit': 'check_request_unit',
        'click .hour_check': 'onlyOne',
        'change .hour_select': 'count_hours_duration',
        'submit #timeoff-form-edit': 'edit_timeoff',
    },

    start: async function () {
        this.request_unit = ""
        this.templates = await rpc('/get/templates')
        console.log(this.templates, "templates 21")
        this.orm = this.bindService("orm");
        var self = this;
        $('#EditLeaveModal').on('show.bs.modal', function (event) {
            self.loadEditTimeoff(event);
        });
    },

    _onClickEdit:async function(event){
        const button = event.currentTarget;
        const attachment_id = button.getAttribute('data-leave-edit-attachment-id');
        const edit_attachment = document.querySelector(`.edit_attachment_${attachment_id}`);
        if(edit_attachment){
            console.log("-=-=-=-=-55555555555555555")
            let response = await $.ajax({
                url: "/get/timeoff_edit_remove",
                method: "GET",
                dataType: 'json',
                data: { id: attachment_id }
            });
            edit_attachment.classList.add('d-none');
        }
        console.log("-=-=-=-=testing",attachment_id)
    },

    sleep: function(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    loadEditTimeoff: async function(event){
        console.log("load cancel timeoff");
        const button = event.relatedTarget;
        const leaveId = button.getAttribute('data-leave-id');
        if(leaveId){
            let response = await $.ajax({
                url: "/get/timeoff_edit",
                method: "GET",
                dataType: 'json',
                data: { id: leaveId }
            });
            console.log("-=-=-=-=-=//-=--=-909090==-=-=-=",response)
            if(response){
                const timeoffeditContainer = document.getElementById('timeoff-edit');
                let text = "";
                for (let key in response) {
                    console.log(`${key}: ${response[key]}`);
                    text +=`<div class="form-control mt-2 edit_attachment_${key}" style="border: 1px solid #dee2e6; margin-left:1px;">
                              <div style="display: inline-block; float: inline-start">${response[key]}</div>
                              <div style="display: inline-block; float: inline-end">
                                    <button type="button" style="font-weight: bold; background: none; color:red; border: none; " data-leave-edit-attachment-id=${key} class="edit_attachment">X</button>
                                </div>
                            </div>`
                }
                timeoffeditContainer.innerHTML = text
            }
        }
        const modalLeaveId = document.querySelector('#leaveIdInput');
        if(modalLeaveId){
            modalLeaveId.value = leaveId;
            rpc('/fetch/hr_leave', {'param1': leaveId}).then(async (data)=>{
                console.log(data, "data 421")
                let timeoff_type = $('#time-off-type-edit');
                console.log(timeoff_type, "timeoff_type before adding option");

                let optionValue = data[0].holiday_status_id[0];
                let optionText = data[0].holiday_status_id[1];

                let existingOption = timeoff_type.find(`option[value='${optionValue}']`);

                if (existingOption.length === 0) {
                    let option = `<option selected="true" value="${optionValue}">${optionText}</option>`;
                    timeoff_type.append(option);
                    console.log(option, "option added");
                    
                } else {
                    timeoff_type.val(optionValue)
                    console.log(existingOption, "option already exists, selected");
                }
                await timeoff_type.trigger('change', {currentTarget: {value: optionValue}})
                await this.sleep(100);
                $('#message-text-edit').val(data[0].name);
                let start_date =  $('#start-date-edit')
                let end_date =  $('#end-date-edit')
                console.log(timeoff_type, "timeoff_type after append");
                console.log('Extracted date:', data[0].date_from.split(' ')[0]);
                console.log(start_date, "$('#start-date-edit')")
                console.log(end_date, "$('#end-date-edit')")
                $('#start-date-edit').val(data[0].date_from.split(' ')[0]);
                $('#end-date-edit').val(data[0].date_to.split(' ')[0]);
                
                console.log(data[0].request_unit_half, "data[0].request_unit_half 454")
                if(data[0].request_unit_half == true){
                    console.log($('#half-day-edit'), "$('#half-day-edit')")
                    $('#half-day-edit').trigger("click")
                }
                if(data[0].request_date_from_period){
                    $('#request_date_from_period_edit').val(data[0].request_date_from_period)
                }
                if(data[0].request_unit_hours == true){
                    console.log($('#custom-hours-edit'), "$('#custom-hours-edit')")
                    $('#custom-hours-edit').trigger("click");
                    $('#start-time-edit').val(data[0].request_hour_from)
                    $('#end-time-edit').val(data[0].request_hour_to)
                }
                $('#leave_duration_edit').val(data[0].duration_display);

                rpc('/check/attachment', {'param1': data[0].holiday_status_id[0]}).then((res)=>{
                    console.log(res, "res 427")
                    let element = document.querySelector('#attachment_edit');
                    if(res){
                        if(element){
                            element.classList.remove('d-none');
                        }
                    }
                    else{
                        if(element){
                            element.classList.add('d-none');
                        }
                    }
                })

                console.log('Updated input value:', $('#start-date-edit').val());
            })

        }
    },

    check_until: function(event){
        let changedElement = event.currentTarget;
        console.log(changedElement.value, "changed element")
    },

    count_duration: async function() {
        let start_time = document.getElementById('start-time-edit')
        let end_time = document.getElementById('end-time-edit')
        let timeoff_error = document.getElementById("timeoff-error-edit")
        timeoff_error.innerHTML = "";
        let from = document.getElementById("start-date-edit")
        let to = document.getElementById("end-date-edit")
        let from_date = new Date(from.value)
        let to_date = new Date(to.value)
        console.log(to_date, from_date, "to date from date 37")
        let hours_checkboxes = document.getElementsByName("request_unit_half_edit")
        console.log(hours_checkboxes, "hour checkbox")
        if(hours_checkboxes.length > 0){
            if(hours_checkboxes[0].checked == true || hours_checkboxes[1].checked == true){
                console.log("checkbox return 20")
                return;
            }
        }
        console.log(from, to, "from to")
        if (from.value && (to.value || (start_time && end_time))) {
            if(!to.value){
                to.value = from.value
            }

            if(this.request_unit == 'day'){
                let duration = await rpc('/get/leave-duration', {'date_from': from.value, 'date_to': to.value, 'leave_type_request_unit': this.request_unit})
                console.log(duration, "duration <<<<<<<<< 45")
                document.getElementById('leave_duration_edit').value = duration[0] + " Days"
            }
            else{
                if(start_time && end_time){
                    var duration = await rpc('/get/leave-duration', {'date_from': from.value, 'date_to': to.value,
                        'hour_from': start_time.value, 'hour_to': end_time.value, 'leave_type_request_unit': this.request_unit})
                    console.log(duration, "duration 62")
                    document.getElementById('leave_duration_edit').value = duration[1] + " Hours"
                    return
                }
                else{
                    var duration = await rpc('/get/leave-duration', {'date_from': from.value, 'date_to': to.value, 'leave_type_request_unit': this.request_unit})
                console.log(duration, "duration <<<<<<<<< 45")
                }
                document.getElementById('leave_duration_edit').value = duration[0] + " Days (" + duration[1] + " Hours)"
            }
        }
    },

    check_request_unit: async function(event) {
        console.log(this, "this");
        var selectedTimeoff = event.currentTarget.value
        console.log(selectedTimeoff, "selectedTimeoff 49")
        if(selectedTimeoff != ""){
            console.log(selectedTimeoff);
            let response = await $.ajax({
                url: "/get/timeoff_type",
                method: "GET",
                dataType: 'json',
                data: { id: selectedTimeoff }
            });
            this.request_unit = response.request_unit
            console.log(response, "response");
            const timeoffContainer = document.getElementById('timeoff-selection-edit')
            const duration_div = document.getElementById('duration-edit')
            console.log(timeoffContainer, "timeoffContainer 446")
            console.log(duration_div, "duration_div 447")
            timeoffContainer.style.display = 'block';
            if (response.request_unit == 'hour') {
                console.log("hours");
                timeoffContainer.innerHTML = this.templates.request_unit_hour_edit;
                duration_div.innerHTML = this.templates.leave_duration_edit;
            }
            else {
                timeoffContainer.innerHTML = this.templates.request_unit_days_edit;
                duration_div.innerHTML = this.templates.leave_duration_edit;
            }
        }
        else{
            const timeoffContainer = document.getElementById('timeoff-selection')
            const duration_div = document.getElementById('duration')
            timeoffContainer.style.display = 'none';
            timeoffContainer.innerHTML = ""
            duration_div.innerHTML = ""
        }
    },

    onlyOne: function(event) {
        var changedElement = event.currentTarget; 
        console.log(changedElement, "changedElement 105");
        var checkboxes = document.getElementsByName("request_unit_half");
        Array.from(checkboxes).forEach((item) => {
            if (item !== changedElement) {
                item.checked = false;
            }
        });
        this.hours_change(changedElement);
    },
    
    hours_change: function(currentValue) {
        console.log(currentValue.value, "current value");
        const leave_duration = document.getElementById('leave_duration_edit');
        let start_date_label = document.getElementById('start-date-label-edit');
        const timeoffContainer = document.getElementById('hour-selection-edit');
        let duration_period = document.getElementById('request_date_from_period_edit')
        let end_date = document.getElementById('end-date-div')
        let end_date_input  = document.getElementById("end-date-edit")
        timeoffContainer.style.display = 'block';
        if (currentValue.value == 'half_day' && currentValue.checked == true) {
            leave_duration.value = "4"
            end_date.value = ""
            end_date.style.display = "none";
            end_date_input.required = false;
            duration_period.value = 'am'
            let period = document.getElementById('request_date_from_period_edit')
            period.style.display = "block";
            timeoffContainer.innerHTML = ``;
            start_date_label.innerHTML = "Date"
        }
        else if (currentValue.value == 'custom_hours' && currentValue.checked == true) {
            end_date.value = ""
            end_date.style.display = "none";
            end_date_input.required = false;
            duration_period.value = ''
            duration_period.style.display = 'none'
            duration_period.required = false;
            leave_duration.value = ""
            timeoffContainer.innerHTML = this.templates.time_selection_edit
        }
        else {
            console.log("else 226")
            end_date.style.display = 'block';
            end_date_input.required = true;
            duration_period.value = ''
            duration_period.style.display = 'none'
            duration_period.required = false;
            timeoffContainer.innerHTML = ""
            leave_duration.value = ""
            this.count_duration()
        }
    },

    count_hours_duration: function(){
        let start_time = document.getElementById('start-time-edit').value
        let end_time = document.getElementById('end-time-edit').value
        console.log(start_time, "start_time")
        console.log(end_time, "end_time")
        if(start_time && end_time > 0){
            this.count_duration()
        }
            
    },

    edit_timeoff: function(e){
        e.preventDefault();
        const formElements = [
            document.getElementById("time-off-type-edit"),
            document.getElementById("leaveIdInput"),
            document.getElementById("request_date_from_period_edit"),
            document.getElementById("start-date-edit"),
            document.getElementById("end-date-edit"),
            document.getElementById("message-text-edit"),
            document.getElementById("start-time-edit"),
            document.getElementById("end-time-edit"),
        ];
        let files_input = document.getElementById("myfile-edit");
        const hourlyLeaveType = document.querySelector("input[name='request_unit_half']:checked");
        let formData = new FormData();
        console.log(formElements, "form elements 772")    
        formElements.forEach(element => {
            if (element && element.value !== "") {
                console.log(element.name, element.value, "element.name, element.value 776")
                formData.append(element.name, element.value);
                console.log(formData, "formDate 778")
            }
        });
    
        if (hourlyLeaveType) {
            formData.append(hourlyLeaveType.name, hourlyLeaveType.value);
        }
    
        for (let i = 0; i < files_input.files.length; i++) {
            formData.append('files', files_input.files[i]);
        }
    
        let unit_half = document.getElementsByName("request_unit_half")
        unit_half.forEach(element => {
            if(element.checked){
                formData.append(element.name, element.value);
            }
        });
        formData.append("edit", true)
        console.log("Form submit");
        console.log(formData);
        let leave_duration = document.getElementById('leave_duration_edit').value
        formData.append("total_days", leave_duration);
        
        fetch('/add/timeoff', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log(response); 
            if (response.status === 400) {
                return response.json().then(errorResponse => {
                    console.log(errorResponse, "errorResponse");
                    if(errorResponse.status == "warning"){
                        document.getElementById("timeoff-error-edit").innerHTML = errorResponse.error;
                    }
                });
            }
            else if(response.status === 200){
                location.reload()
            }
            return response.json(); 
        })
        .catch(error => console.error('Error:', error));
    }
})