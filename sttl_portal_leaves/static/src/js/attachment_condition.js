/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

$(document).ready(function () {
    $('#time-off-type').on('click', function (event) {
        event.preventDefault();
        var selectedValue = $('select[name="holiday_status_id"]').val();
        var element = document.querySelector('.selectfile');
        rpc('/check/attachment', {'param1': selectedValue}).then((res)=>{
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
    });
});

$(document).ready(function () {
    $('#time-off-type-edit').on('click', function (event) {
        event.preventDefault();
        var selectedValue = $('select[id="time-off-type-edit"]').val();
        console.log(selectedValue, "selected value 30")
        var element = document.querySelector('#attachment_edit');
        rpc('/check/attachment', {'param1': selectedValue}).then((res)=>{
            console.log(res, "res 32")
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
    });
});