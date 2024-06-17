$(function(){

/** BORA-JS **/
	
});


function parse_icon(key, value, timestamp, invalid) {
    //console.log(invalid); // invalid value is in milliseconds
    //console.log("Inside parse_icon");
    //console.log(key,value,timestamp, invalid);

    var data_oncondition = $("#" + key).attr("data-oncondition");
    var data_icon_type = $("#" + key).attr("data-icon-type");
    //var data_offcondition = $("#" + key).attr("data-offcondition");

    let condition = data_oncondition;

    let currentTime = new Date();
    let currentTimeMillis = currentTime.getTime();

    var delta = (currentTimeMillis - timestamp) / 1000.0;
    // since delta is converted to seconds, we need to convert invalid to seconds as well
    invalid = invalid / 1000.0;

    // Parse the condition
    const match = condition.match(/([><=!]=?|==)\s*(\d+)/);
    if (match) {
        const operator = match[1];
        const threshold = parseInt(match[2], 10);

        // Evaluate the condition
        let result;
        switch (operator) {
            case '>':
                result = value > threshold;
                break;
            case '<':
                result = value < threshold;
                break;
            case '>=':
                result = value >= threshold;
                break;
            case '<=':
                result = value <= threshold;
                break;
            case '==':
                result = value == threshold;
                break;
            case '!=':
                result = value != threshold;
                break;
            default:
                throw new Error("Invalid operator");
        }

        if (result) {
            //console.log("Condition is True");
            $("#" + key + "> img").attr('src', '/static/' + data_icon_type + '_green.png');
        } else {
            //console.log("Condition is False");
            $("#" + key + "> img").attr('src', '/static/' + data_icon_type + '_red.png');
        }
    } else {
        //console.log("Invalid condition format");
        $("#" + key + "> img").attr('src', '/static/' + data_icon_type + '_inactive.png');
    }

    if (invalid != undefined && invalid < delta) {
        $("#" + key + "> img").attr('src', '/static/' + data_icon_type + '_inactive.png');
    }

    $("#"+key).attr('tooltip',  key + "\nDeltaTime: " + parseFloat(delta).toFixed(3) + " s (" + parseFloat(delta / 60.0).toFixed(3) + " min)");
}
