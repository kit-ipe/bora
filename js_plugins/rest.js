function rest_set_query(id, url, value) {
    var myurl = url + "?v=" + value;

    $.ajax({
        url: myurl,
        type: 'GET',
        crossDomain: true,
        success: function (response) {
            console.log(response);
        },
        error: function () {
            console.log("Error.")
        }
    });
}

// function to handle success
function success() {
    var data = JSON.parse(this.responseText); //parse the string to JSON
    console.log(data);
    $( "#" + data["device_parameter"] ).find( "img" ).attr("src","/static/commbit_green.svg");
    $( "#" + data["device_parameter"] ).find( "input" ).val(data["value"]);
}

// function to handle error
function error(err) {
    console.log('Request Failed', err); //error details will be in the "err" object
}


function rest_get_query(id, url) {
    $( "#" + id ).find( "img" ).attr("src","/static/commbit_red.svg");

    var xhr = new XMLHttpRequest(); //invoke a new instance of the XMLHttpRequest
    xhr.onload = success; // call success function if request is successful
    xhr.onerror = error;  // call error function if request failed
    //xhr.open('GET', 'https://api.github.com/users/manishmshiva'); // open a GET request
    xhr.open('GET', 'http://localhost:18080/api/v1/dma/' + id ); // open a GET request
    xhr.send(); // send the request to the server.
}


$("input").on('keypress',function(e) {
    if(e.which == 13) {
        console.log($(this).closest('div').attr('id'));
        console.log($(this).closest('div').attr('data-url'));
        console.log($(this).val());
        var id = $(this).closest('div').attr('id');
        var url = $(this).closest('div').attr('data-url');
        var value = $(this).val();
        rest_set_query(id, url, value);
    }
});

$( window ).on( "load", function() {
  console.log("This is rest.js onload");
  $('[data-type="rest"]').each(function(){
    // Do stuff with each div
    console.log($(this).closest('div').attr('id'));
    console.log($(this).closest('div').attr('data-url'));
    console.log($(this).val());
    var id = $(this).closest('div').attr('id');
    var url = $(this).closest('div').attr('data-url');
    rest_get_query(id, url);
});
} );
