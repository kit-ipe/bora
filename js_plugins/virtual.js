$(function(){

    /** BORA-JS **/
});

/*
var retval = eval( "parse_" + response[key]["widget"].replace(/-/g, "_") + "('" + key + "','" + response[key]["value"] + "','" + response[key]["timestamp"] +"','" + response[key]["invalid"] + "')" );
*/

function parse_virtual(id, response) {
    //console.log(invalid); // invalid value is in milliseconds
    //console.log("Inside parse_virtual()");
    //console.log(id);

    var key = $("#" + id).attr("data-virtual-id");
    //console.log(key);
    //console.log(response);
    var value = response[key]["value"];
    var timestamp = response[key]["timestamp"];
    var invalid = response[key]["invalid"];

    let currentTime = new Date();
    let currentTimeMillis = currentTime.getTime();

    var data_decimal_numbers = parseInt($("#" + id).attr("data-decimal-numbers"));
    var data_smaller_than = $("#" + id).attr("data-smaller-than");
    var data_larger_than = $("#" + id).attr("data-larger-than");
    var data_exp = $("#" + id).attr("data-exp");
    var data_formula = $("#" + id).attr("data-formula");


    var delta = (currentTimeMillis - timestamp) / 1000.0;
    // since delta is converted to seconds, we need to convert invalid to seconds as well
    invalid = invalid / 1000.0;


    var myformula = data_formula.trim();
    var data = myformula;
    var re= /\[(.*?)\]/g;
    var buffer = []
    for(m = re.exec(data); m; m = re.exec(data)){
        buffer.push(m[1]);
    }

    var finalstring = "";
    var pattern = /\[(.*?)\]/g;
    var teststring = myformula.split(/[\[\]]+/);

    for (var i = 0; i < teststring.length; i++) {
        var val = "";            
        if (teststring[i] in response) {
            val = response[teststring[i]]["value"];
        } else {
            val = teststring[i];
        }
        finalstring += val;
        finalstring += " ";
    }
                
    finalstring = finalstring.trim();
    console.log("(line code delay) suppress error from math.js");
    console.log("(line code delay) suppress error from math.js");

    var value = math.round(math.eval(finalstring),parseInt(data_decimal_numbers));


    if (data_smaller_than != undefined && data_larger_than != undefined) {
    
        if (value > data_smaller_than && value < data_larger_than) {
            $("#" + key + "> .value").css('color', 'green');
            $("#" + key + "> .unit-name").css('color', 'green');
        } else if (data_smaller_than == '' && data_larger_than == '') {
            $("#" + key + "> .value").css('color', 'green');
            $("#" + key + "> .unit-name").css('color', 'green');
        } else if (value < data_smaller_than && data_larger_than == '') {
            $("#" + key + "> .value").css('color', 'red');
            $("#" + key + "> .unit-name").css('color', 'red');
        } else if (value > data_smaller_than && data_larger_than == '') {
            $("#" + key + "> .value").css('color', 'green');
            $("#" + key + "> .unit-name").css('color', 'green');
        } else if (value > data_larger_than && data_smaller_than == '') {
            $("#" + key + "> .value").css('color', 'red');
            $("#" + key + "> .unit-name").css('color', 'red');
        } else if (value < data_larger_than && data_smaller_than == '') {
            $("#" + key + "> .value").css('color', 'green');
            $("#" + key + "> .unit-name").css('color', 'green');
        } else {
            // value < data_smaller_than && value > data_larger_than
            $("#" + key + "> .value").css('color', 'red');
            $("#" + key + "> .unit-name").css('color', 'red');
        }
    }


    if (data_exp != undefined && data_exp == "true") {
        if (data_decimal_numbers != undefined && data_decimal_numbers > 0) {
            value = parseFloat(value).toExponential(data_decimal_numbers);
        } else {
            value = parseFloat(value).toExponential();
        }
    } else {
        // when data_exp == false
        if (data_decimal_numbers != undefined && data_decimal_numbers >= 0) {
            if (value >= 0) {
                value = (Math.round(value * 100) / 100).toFixed(data_decimal_numbers);
            } else {
                // negative value
                value = ((value * 100) / 100).toFixed(data_decimal_numbers);
            }
        }
    }

    if (invalid != undefined && invalid < delta) {
        $("#" + id + "> .value").css('color', 'grey');
        $("#" + id + "> .unit-name").css('color', 'grey');
    }

    $("#"+id).attr('tooltip',  key + "\nDeltaTime: " + parseFloat(delta).toFixed(3) + " s (" + parseFloat(delta / 60.0).toFixed(3) + " min)");

    $("#" + id + " > .value").text(value);
}

var win_width = $(document).width();
var win_height = $(document).height();

$(".virtualbox").hover(function(){
    var trend_time_end = Math.floor(Date.now() / 1000);
    var trend_time_start = trend_time_end - 3600;
    var key = $(this).attr('data-virtual-id');
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
