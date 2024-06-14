$(function(){

/** BORA-JS **/
	
});

function parse_integer_to_string(key, value, timestamp, invalid) {
    let currentTime = new Date();
    let currentTimeMillis = currentTime.getTime();
    var delta = (currentTimeMillis - timestamp) / 1000.0;
    // since delta is converted to seconds, we need to convert invalid to seconds as well
    invalid = invalid / 1000.0;

    //data-int-to-str
    var data_int_to_str = $("#" + key).attr("data-int-to-str");
    
    var str = data_int_to_str;
    str = str.replace(/'/g, '"');
    var tmp_value;
    let jsonObj = JSON.parse(str);

    if( jsonObj[value] === undefined ) {
        tmp_value = "UNDEFINED";
    } else {
        tmp_value = jsonObj[value];
    }

    if (invalid != undefined && invalid < delta) {
        $("#" + key + "> .value").css('color', 'grey');
        $("#" + key + "> .unit-name").css('color', 'grey');
    }

    $("#"+key).attr('tooltip',  key + "\nDeltaTime: " + parseFloat(delta).toFixed(3) + " s (" + parseFloat(delta / 60.0).toFixed(3) + " min)");

    return tmp_value;
}
