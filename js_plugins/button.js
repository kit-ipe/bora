// function to handle success
function restb_success() {
    var data = JSON.parse(this.responseText); //parse the string to JSON
    console.log(data);
    
    $( "#" + data["device_parameter"] ).find( "img" ).attr("src","/static/commbit_green.svg");
    $( "#" + data["device_parameter"] ).find( "input" ).val(data["value"]);
}

function restb_error(err) {
    console.log('Request Failed', err); //error details will be in the "err" object
}

function restb_get_query(id, url) {
    $( "#" + id ).find( "img" ).attr("src","/static/commbit_red.svg");
    var xhr = new XMLHttpRequest();
    xhr.onload = restb_success;
    xhr.onerror = restb_error;
    xhr.open('GET', url );
    xhr.send();
}

$('button').on('click', function(){
    var id = $(this).parent().attr('id');
    var url = $(this).closest('div').attr('data-url');
    console.log(id, url);
    restb_get_query(id, url);
})


