// When files are selected for upload, display selection with form fields.
$('#pics').bind('change', function() {
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
    // Number of pics selected for upload.
    var selected = $('.selected').length;
    // Number of pics selected for deletion.
    var deleted = $('input:checkbox:checked').length;
    // Number of pics already in gallery post.
    var gallery_pics = $('.pic').length;
    if(gallery_pics + selected - deleted > 8) {
        flash("Posts cannot have more than 8 pictures.", 'warning');
        $('#pics').val('');
        $('.selected').remove();
        event.preventDefault();
    }
});
