$(function(){

    /** BORA-JS **/
});


function parse_calc(key, response) {
    //console.log(invalid); // invalid value is in milliseconds
    
    //console.log("Inside parse_calc()");

    var data_decimal_numbers = parseInt($("#" + key).attr("data-decimal-numbers"));
    var data_smaller_than = $("#" + key).attr("data-smaller-than");
    var data_larger_than = $("#" + key).attr("data-larger-than");
    var data_formula = $("#" + key).attr("data-formula");

    //console.log(data_decimal_numbers);
    //console.log(data_smaller_than);
    //console.log(data_larger_than);
    //console.log(data_formula);
    //console.log(response);

    var myformula = data_formula.trim();

    var data = myformula;
    var re= /\[(.*?)\]/g;
    var buffer = []
    for(m = re.exec(data); m; m = re.exec(data)){
        buffer.push(m[1]);
    }
    //console.log("Debug:");
    //console.log(buffer);
    
    var finalstring = "";
    var pattern = /\[(.*?)\]/g;
    var teststring = myformula.split(/[\[\]]+/);
    //console.log("Test String");
    //console.log(teststring);
    //console.log(finalstring);
                
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

    //console.log("My Value");
    //console.log(value);

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

    $("#" + key + " > .value").text(value);
}
