$(function(){

    /** BORA-JS **/
});


function parse_calc(key, response) {
    //console.log(invalid); // invalid value is in milliseconds
    
    console.log("Inside parse_calc()");

    var data_decimal_numbers = parseInt($("#" + key).attr("data-decimal-numbers"));
    var data_smaller_than = $("#" + key).attr("data-smaller-than");
    var data_larger_than = $("#" + key).attr("data-larger-than");
    var data_formula = $("#" + key).attr("data-formula");

    console.log(data_decimal_numbers);
    console.log(data_smaller_than);
    console.log(data_larger_than);
    console.log(data_formula);

    console.log(response);

    //var myformula = $(this).attr('data-formula').trim();
    var myformula = data_formula.trim();

    var data = myformula;
    var re= /\[(.*?)\]/g;
    var buffer = []
    for(m = re.exec(data); m; m = re.exec(data)){
        buffer.push(m[1]);
    }
    console.log("Debug:");
    console.log(buffer);
    
    var finalstring = "";
    var pattern = /\[(.*?)\]/g;
    var teststring = myformula.split(/[\[\]]+/);
    console.log("Test String");
    console.log(teststring);
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
    console.log("Final String");
    console.log(finalstring);

    var value = math.round(math.eval(finalstring),parseInt(data_decimal_numbers));

    console.log("My Value");
    console.log(value);

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

    /*
                var myvalue = math.round(math.eval(finalstring),2);
                myvalue = myvalue.toFixed($("#" + this.id).attr('data-decimal'));
 		    	set_color = "green";
                console.log(myvalue);
                $(".varval", "#" + this.id).text(myvalue);
                var condition_attr = $("#" + this.id).attr('data-cond');
                var lesser_attr = $("#" + this.id).attr('data-lesser');
                var larger_attr = $("#" + this.id).attr('data-larger');
  		        //console.log(condition_attr);
                if (condition_attr) {
 			        if (myvalue == condition_attr) {
 			            set_color = "red";
      		        }
		        }
 		    	if (lesser_attr) {
 			        if (parseFloat(myvalue) < parseFloat(lesser_attr)) {
 			            set_color = "red";
      		        }
		        }
  		        if (larger_attr) {
 			        if (parseFloat(myvalue) > parseFloat(larger_attr)) {
 			            set_color = "red";
      			    }
		        }
		        $(".varval", "#" + this.id).css("color", set_color);
		        $(".unit_title", "#" + this.id).css("color", set_color);
                }    
    */

    /*
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
    */
}
