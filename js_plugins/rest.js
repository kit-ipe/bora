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
