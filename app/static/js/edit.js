/**
 * Form setup, validation, and manipulation.
 */

// Handle click events for 'up' position button.
var ups = document.getElementsByClassName('up');
for (var i = 0; i < ups.length; i++) {
    ups[i].addEventListener('click', function(event) {
        var elem1 = event.target.parentNode.parentNode.parentNode;
        var elem2 = elem1.previousElementSibling;
        if (elem2 != 'null') {
            var pos1 = elem1.getElementsByClassName('position-field')[0];
            var pos2 = elem2.getElementsByClassName('position-field')[0];
            var swap = pos1.value;
            pos1.value = pos2.value;
            pos2.value = swap;
            field.insertBefore(elem1, elem2);
        }
    }, false);
};

// Handle click events for 'down' position button.
var downs = document.getElementsByClassName('down');
for (var i = 0; i < downs.length; i++) {
    downs[i].addEventListener('click', function(event) {
        var elem1 = event.target.parentNode.parentNode.parentNode;
        var elem2 = elem1.nextElementSibling;
        if (elem2 != 'null') {
            var pos1 = elem1.getElementsByClassName('position-field')[0];
            var pos2 = elem2.getElementsByClassName('position-field')[0];
            var swap = pos1.value;
            pos1.value = pos2.value;
            pos2.value = swap;
            field.insertBefore(elem2, elem1);
        }
    }, false);
};
    
// Creates a new picture form and appends it to list for editing.
function appendPic(filename) {
    if (typeof filename === 'undefined') {
        return;
    }
    // Container div.
    var div = document.createElement('div');
    div.className = 'selected col-xs-12 col-sm-6 col-md-6 col-lg-6';
    // Placeholder form div.
    var pic_placeholder = document.createElement('div');
    pic_placeholder.className = 'pic col-xs-1';
    var pic_img = document.createElement('div');
    pic_img.className = 'pic-img col-xs-12';
    var img = document.createElement('img');
    img.className = 'img-responsive';
    // Form div.
    var form = document.createElement('div');
    form.className = 'form col-xs-11';
    // Title div.
    var title = document.createElement('div');
    title.className = 'form-title form-group';
    // Title label.
    var title_label = document.createElement('label');
    title_label.innerHTML = "Title";
    // Title input.
    var title_input = document.createElement('input');
    title_input.className = "form-control title";
    title_input.setAttribute('type', 'text');
    title_input.setAttribute('value', filename);
    title_input.setAttribute('name', filename);
    // Cover div.
    var radio = document.createElement('div');
    radio.className = 'form-cover form-group';
    // Cover label.
    var radio_label = document.createElement('label');
    radio_label.innerHTML = "Cover:";
    // Cover input.
    var radio_input = document.createElement('input');
    radio_input.setAttribute('type', 'radio');
    radio_input.setAttribute('value', filename);
    radio_input.setAttribute('name', 'choice');
    // Position paragraph.
    var position = document.createElement('div');
    position.className = 'form-position form-group';
    // Position label.
    var position_label = document.createElement('label');
    position_label.innerHTML = "Position:";
    // Position input.
    var position_input = document.createElement('input');
    position_input.className = 'position-field';
    position_input.setAttribute('type', 'text');
    position_input.setAttribute('style', 'display: none;');
    var pic_fields = document.getElementsByClassName('position-field');
    if (pic_fields == 'null') {
        position_input.setAttribute('value', 1);
    } else {
        position_input.setAttribute('value', pic_fields.length + 1);
    }
    position_input.setAttribute('size', 1);
    position_input.setAttribute('readonly', '');
    // Added suffix to prevent name conflict with title.
    position_input.setAttribute('name', filename + '-pos');
    // Position up button.
    var position_up = document.createElement('i');
    position_up.className = 'up fa fa-caret-square-o-up';
    // Add up event listener.
    position_up.addEventListener('click', function(event) {
        var elem1 = event.target.parentNode.parentNode.parentNode;
        var elem2 = elem1.previousElementSibling;
        if (elem2 != 'null') {
            var pos1 = elem1.getElementsByClassName('position-field')[0];
            var pos2 = elem2.getElementsByClassName('position-field')[0];
            var swap = pos1.value;
            pos1.value = pos2.value;
            pos2.value = swap;
            field.insertBefore(elem1, elem2);
        }
    }, false);
    // Position down link.
    var position_down = document.createElement('i');
    position_down.className = 'down fa fa-caret-square-o-down';
    // Add down event listener.
    position_down.addEventListener('click', function(event) {
        var elem1 = event.target.parentNode.parentNode.parentNode;
        var elem2 = elem1.nextElementSibling;
        if (elem2 != 'null') {
            var pos1 = elem1.getElementsByClassName('position-field')[0];
            var pos2 = elem2.getElementsByClassName('position-field')[0];
            var swap = pos1.value;
            pos1.value = pos2.value;
            pos2.value = swap;
            field.insertBefore(elem2, elem1);
        }
    }, false);
    // Assemble!
    position.appendChild(position_label);
    position.appendChild(position_input);
    position.appendChild(position_up);
    position.appendChild(position_down);
    radio.appendChild(radio_label);
    radio.appendChild(radio_input);
    form.appendChild(title_label);
    form.appendChild(title_input);
    form.appendChild(radio);
    form.appendChild(position);
    pic_img.appendChild(img);
    pic_placeholder.appendChild(pic_img);
    div.appendChild(pic_placeholder);
    div.appendChild(form);
    // Add to picfield.
    document.getElementById('picfield').appendChild(div);
    pushFooter();
}

// When files are selected for upload, display selection with form fields.
$('#pics').bind('change', function() {
    $('.selected').remove();
    $.each(this.files, function(index, value) {
        appendPic(value.name);
    });
});

// Shuffles around pic forms and updates position form field.
var field = document.getElementById('picfield');
var pos_forms = document.getElementsByClassName('position-form');
for (var i = 0; i < pos_forms.length; i++) {
    // Attach click event listener to picture forms.
    // Used for moving forms around.
    clickEventListener(pos_forms[i]);
}

// Ensures that radio is checked when form is submitted.
$('form').submit(function(event) {
    if ($('input:radio[name=choice]').is(':checked') === false) {
        $('input:radio:first').attr('checked', true);
    }
    // Number of pics selected for upload.
    var selected = $('.selected').length;
    // Number of pics selected for deletion.
    var deleted = $('input:checkbox:checked').length;
    // Number of pics already in gallery post.
    var gallery_pics = $('.pic').length;
    if (gallery_pics + selected - deleted > 8) {
        event.preventDefault();
        $('.selected').remove();
        flash("Posts cannot have more than 8 pictures.", 'warning');
    } else {
        return;
    }
});
