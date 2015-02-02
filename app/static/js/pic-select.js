// When files are selected for upload, display selection with form fields.
$('#pics').bind('change', function() {
    /*
    $('#selection').empty();
    $.each(this.files, function(index, value) {
        $('#selection').append("<li>" + value.name +
                "Select as cover: <input type='radio' value='" + 
                value.name + "' name='choice'></input></li>");
    });
    */
    $('.selected').remove();
    $.each(this.files, function(index, value) {
        $('#picfield').append(
            '<div class="selected col-xs-6 col-sm-6 col-md-6 col-lg-6">' + 
              '<div class="col-xs-6 col-sm-6 col-md-6 col-lg-6">' +
                '<a href=""' + 'title="' + value.name + '" class="thumbnail"' +
                    'onclick="return false">' + '<img src=""' + 
                    'alt="' + value.name + '"' +
                      'class="img-responsive img-rounded">' +
                '</a></div>' +
              '<div class="col-xs-6 col-sm-6 col-md-6 col-lg-6">' +
                '<label>Title</label>' +
                '<input type="text" value="' + value.name + 
                '" name="' + value.name + '"></input>' +
                '<p>' +
                  '<label>Select as cover:</label>' +
                    '<input type="radio" value="' + value.name + '"' +
                        'name="choice">' +
                    '</input></p></div></div>');
    });
});

// Ensures that radio is checked when form is submitted.
$('form').submit(function(event) {
    if($('input:radio[name=choice]').is(':checked') === false) {
        $('input:radio:first').attr('checked', true);
    }
    if($('.selected').length + $('.pic').length > 8) {
        :wq

    }
});
