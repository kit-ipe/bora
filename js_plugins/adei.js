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

function parse_adei(key, value, timestamp, invalid) {
    //console.log(invalid); // invalid value is in milliseconds
    
    let currentTime = new Date();
    let currentTimeMillis = currentTime.getTime();

    var data_decimal_numbers = parseInt($("#" + key).attr("data-decimal-numbers"));
    var data_smaller_than = $("#" + key).attr("data-smaller-than");
    var data_larger_than = $("#" + key).attr("data-larger-than");
    var data_exp = $("#" + key).attr("data-exp");


    //var timestamp = response[key]["timestamp"];
    //var invalid = response[key]["invalid"];
    //var value = response[key]["value"];

    var delta = (currentTimeMillis - timestamp) / 1000.0;
    // since delta is converted to seconds, we need to convert invalid to seconds as well
    invalid = invalid / 1000.0;


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

    if (invalid != undefined && invalid < delta) {
        $("#" + key + "> .value").css('color', 'grey');
        $("#" + key + "> .unit-name").css('color', 'grey');
    }

    $("#"+key).attr('tooltip',  key + "\nDeltaTime: " + parseFloat(delta).toFixed(3) + " s (" + parseFloat(delta / 60.0).toFixed(3) + " min)");

    return value;
}

