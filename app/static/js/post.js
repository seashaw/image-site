function clickEventListener(pos_form) {
    var children = pos_form.children;
    children[2].addEventListener("click", function(event) {
        event.preventDefault();
        var elem1 = event.target.parentNode.parentNode.parentNode;
        var elem2 = elem1.previousElementSibling;
        if (elem2 != 'null') {
            var pos1 = elem1.querySelector('.position-field');
            var pos2 = elem2.querySelector('.position-field');
            var swap = pos1.value;
            pos1.value = pos2.value;
            pos2.value = swap;
            field.insertBefore(elem1, elem2);
        }
    }, false);
    children[3].addEventListener("click", function(event) {
        event.preventDefault();
        var elem1 = event.target.parentNode.parentNode.parentNode;
        var elem2 = elem1.nextElementSibling;
        if (elem2 != 'null') {
            var pos1 = elem1.querySelector('.position-field');
            var pos2 = elem2.querySelector('.position-field');
            var swap = pos1.value;
            pos1.value = pos2.value;
            pos2.value = swap;
            field.insertBefore(elem2, elem1);
        }
    }, false);
}

function appendPic(filename) {
    if (typeof filename === 'undefined') {
        return;
    }
    // Container div.
    var div = document.createElement('div');
    div.className = 'selected col-xs-6 col-sm-6 col-md-6 col-lg-6';
    // Thumbnail div.
    var thumb = document.createElement('div');
    thumb.className = 'col-xs-6 col-sm-6 col-md-6 col-lg-6';
    // Thumbnail link.
    var anchor = document.createElement('a');
    anchor.setAttribute('title', filename);
    anchor.setAttribute('onlick', 'return false');
    anchor.className = 'thumbnail';
    // Thumbnail image.
    // No image, mostly for page consistency.
    var image = document.createElement('img');
    image.setAttribute('alt', filename);
    image.setAttribute('src', '');
    image.className = 'img-responsive img-rounded';
    // Form div.
    var form = document.createElement('div');
    form.className = 'col-xs-6 col-sm-6 col-md-6 col-lg-6';
    // Title label.
    var title_label = document.createElement('label');
    title_label.innerHTML = "Title";
    // Title input.
    var title_input = document.createElement('input');
    title_input.className = "title";
    title_input.setAttribute('type', 'text');
    title_input.setAttribute('value', filename);
    title_input.setAttribute('name', filename);
    // Radio paragraph.
    var radio = document.createElement('p');
    // Radio label.
    var radio_label = document.createElement('label');
    radio_label.innerHTML = "Select as cover:";
    // Radio input.
    var radio_input = document.createElement('input');
    radio_input.setAttribute('type', 'radio');
    radio_input.setAttribute('value', filename);
    radio_input.setAttribute('name', 'choice');
    // Position paragraph.
    var position = document.createElement('p');
    position.className = 'position-form';
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
    // Position up link.
    var position_up = document.createElement('a');
    position_up.className = 'up';
    position_up.setAttribute('href', '');
    position_up.setAttribute('onclick', 'return false;');
    position_up.innerHTML = "up";
    // Position down link.
    var position_down = document.createElement('a');
    position_down.className = 'down';
    position_down.setAttribute('href', '');
    position_down.setAttribute('onclick', 'return false;');
    position_down.innerHTML = "down";
    // Assemble!
    anchor.appendChild(image);
    thumb.appendChild(anchor);
    position.appendChild(position_label);
    position.appendChild(position_input);
    position.appendChild(position_up);
    position.appendChild(position_down);
    // Attach click handler.
    clickEventListener(position);
    radio.appendChild(radio_label);
    radio.appendChild(radio_input);
    form.appendChild(title_label);
    form.appendChild(title_input);
    form.appendChild(radio);
    form.appendChild(position);
    div.appendChild(thumb);
    div.appendChild(form);
    // Add to picfield.
    document.getElementById('picfield').appendChild(div);
}

// When files are selected for upload, display selection with form fields.
$('#pics').bind('change', function() {
    $('.selected').remove();
    $.each(this.files, function(index, value) {
        appendPic(value.name);
    });
});

var field = document.getElementById('picfield');
// Shuffles around pic forms and updates position form field.
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
