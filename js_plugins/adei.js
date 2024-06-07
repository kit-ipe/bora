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
    } else {
        $("#" + key + "> .value").css('color', 'green');
        $("#" + key + "> .unit-name").css('color', 'green');
    }

    if (data_larger_than != undefined && value > data_larger_than) {
        $("#" + key + "> .value").css('color', 'red');
        $("#" + key + "> .unit-name").css('color', 'red');
    } else {
        $("#" + key + "> .value").css('color', 'green');
        $("#" + key + "> .unit-name").css('color', 'green');
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


var win_width = $(document).width();
var win_height = $(document).height();

$(".databox").hover(function(){
    var trend_time_end = Math.floor(Date.now() / 1000);
    var trend_time_start = trend_time_end - 3600;
    var key = $(this).attr('id');
    var data_adei = "https://adei-katrin.kaas.kit.edu/adei/";
    var data_query = $("#" + key).attr('data-query');

    data_query = data_query.split("?")[1];

    const urlParams = new URLSearchParams("?"+data_query);

    var output_query = "db_server="+urlParams.get('db_server')+"&db_name="+urlParams.get('db_name')+"&db_group="+urlParams.get('db_group')+"&db_mask="+urlParams.get('db_mask'); 

    if ($("#" + key).attr('data-trend') == "true") {
        $('#'+key + '> .popup').remove();
        $('#'+ key).append('<span class="popup" style="top:0; left:250px;"><img src="' + data_adei + 'services/getimage.php?' + output_query + '&window='+ trend_time_start.toString() +'-'+ trend_time_end.toString() + '&frame_width=600&frame_height=400" width="600px" height="400px"/></span>');
        var key_left = parseInt($("#" + key).css("left"));
	    var pos_left = key_left + 850;
        var key_top = parseInt($("#" + key).css("top"));
        var pos_top = key_top + 400;
        if(pos_left > win_width) {
            $("#" + key + " .popup").css({
	        'right':'250px',
	        'left': ''
	    });
        }
        if(pos_top > win_height) {
            $("#" + key + " .popup").css({
                'bottom':'0px',
                'top': ''
            });
        }
    }
});

function open_adei_page(key) {
    var data_link_adei = $("#" + key).attr('data-link-adei');

    var data_query = $("#" + key).attr('data-query');
    data_query = data_query.split("?")[1];
    const urlParams = new URLSearchParams("?"+data_query);
    var output_url = "https://adei-katrin.kaas.kit.edu/adei/#module=graph&db_server="+urlParams.get('db_server')+"&db_name="+urlParams.get('db_name')+"&db_group="+urlParams.get('db_group')+"&db_mask="+urlParams.get('db_mask')+"&experiment=-&window=86400&module=graph&virtual=srctree&srctree=&infomod=legend";

    if (data_link_adei != undefined && data_link_adei == "true") {    
        window.open(output_url, '_blank');
    } else {
        return;
    }
}
