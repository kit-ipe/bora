$(function(){

/** BORA-JS **/


});

/*
data-decimal-numbers="{{ data['style'][key]['div']['data-decimal-numbers'] }}"
data-smaller-than="{{ data['style'][key]['div']['data-smaller-than'] }}"
data-larger-than="{{ data['style'][key]['div']['data-larger-than'] }}"
data-exp="{{ data['style'][key]['div']['data-exp'] }}"
data-link-adei="{{ data['style'][key]['div']['data-link-adei'] }}"
data-trend="{{ data['style'][key]['div']['data-trend']
*/

function parse_adei(key, value) {
    var data_decimal_numbers = parseInt($("#" + key).attr("data-decimal-numbers"));
    var data_smaller_than = $("#" + key).attr("data-smaller-than");
    var data_larger_than = $("#" + key).attr("data-larger-than");
    var data_exp = $("#" + key).attr("data-exp");
    
    if (data_decimal_numbers != undefined && data_decimal_numbers > 0) {
        value = (Math.round(value * 100) / 100).toFixed(data_decimal_numbers);
    }

    if (data_smaller_than != undefined && value < data_smaller_than) {
        $("#" + key + "> .value").css('color', 'red');
        $("#" + key + "> .unit-name").css('color', 'red');
    }

    if (data_larger_than != undefined && value > data_larger_than) {
        $("#" + key + "> .value").css('color', 'red');
        $("#" + key + "> .unit-name").css('color', 'red');
    }

    if (data_exp != undefined && data_exp == "true") {
        if (data_decimal_numbers != undefined && data_decimal_numbers > 0) {
            value = parseFloat(value).toExponential(data_decimal_numbers);
        } else {
            value = parseFloat(value).toExponential();
        }
    }

    return value;
}

