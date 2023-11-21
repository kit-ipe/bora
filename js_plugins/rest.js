function rest_set_query(id, url, value) {
    $( "#" + id ).find( "img" ).attr("src","/static/commbit_red.svg");

    var data = {};
    data.value = value;
    var json = JSON.stringify(data);

    var xhr = new XMLHttpRequest();
    xhr.onload = success_set;
    xhr.onerror = error;
    xhr.open('PUT', url);
    xhr.send(json);
}

// function to handle success
function success() {
    var data = JSON.parse(this.responseText); //parse the string to JSON
    $( "#" + data["device_parameter"] ).find( "img" ).attr("src","/static/commbit_green.svg");
    $( "#" + data["device_parameter"] ).find( "input" ).val(data["value"]);
}

function success_set() {
    var data = JSON.parse(this.responseText); //parse the string to JSON
    $("#" + data["device_parameter"] ).find( "img" ).attr("src","/static/commbit_green.svg");
    $("#" + data["device_parameter"] ).find( "input" ).val(data["value"]);
  
    $('[data-type="rest"]').each(function(){
        var id = $(this).closest('div').attr('id');
        var url = $(this).closest('div').attr('data-url');
        rest_get_query(id, url);
    });
}

function error(err) {
    console.log('Request Failed', err); //error details will be in the "err" object
}

function rest_get_query(id, url) {
    $( "#" + id ).find( "img" ).attr("src","/static/commbit_red.svg");
    var xhr = new XMLHttpRequest();
    xhr.onload = success;
    xhr.onerror = error;
    xhr.open('GET', url );
    xhr.send();
}

$("input").on('keypress',function(e) {
    if (e.which == 13) {
        var id = $(this).closest('div').attr('id');
        var url = $(this).closest('div').attr('data-url');
        var value = $(this).val();
        rest_set_query(id, url, value);
    }
});

$(window).on("load", function() {
    $('[data-type="rest"]').each(function(){
        var id = $(this).closest('div').attr('id');
        var url = $(this).closest('div').attr('data-url');
        rest_get_query(id, url);
    });
});
