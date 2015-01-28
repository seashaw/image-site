﻿// When files are selected for upload, display selection with form fields.
$('#pics').bind('change', function() {
    $('#selection').empty();
    $.each(this.files, function(index, value) {
        $('#selection').append("<li>" + value.name +
                "<p>Select as cover: </p><input type='radio' value='" + 
                value.name + "' name='choice'></input></li>");
    });
});

// Ensures that a radio is checked when form is submitted.
$('form').submit(function(event) {
    if($('input:radio[name=choice]').is(':checked') === false) {
        $('input:radio:first').attr('checked', true);
    }
});
