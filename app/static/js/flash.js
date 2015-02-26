function flash(message, category) {
    if (typeof category === 'undefined') {
        var div_class = 'alert alert-message alert-dismissable';
    } else {
        var div_class = 'alert alert-' + category + ' alert-dismissable';
    }
    // Container div.
    var div = document.createElement('div');
    div.className = div_class;
    div.setAttribute('role', 'alert');
    // Button.
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'close';
    button.setAttribute('data-dismiss', 'alert');
    // Glyphicon for button.
    var glyph = document.createElement('span');
    glyph.className = 'glyphicon glyphicon-remove';
    glyph.setAttribute('aria-hidden', 'true');
    // Span for Screen Readers.
    var screen_reader = document.createElement('span');
    screen_reader.className = 'sr-only';
    screen_reader.innerHTML = "Close";
    // Message paragraph;
    var msg = document.createElement('p');
    msg.innerHTML = message;
    // Assemble!
    button.appendChild(glyph);
    button.appendChild(screen_reader);
    div.appendChild(button);
    div.appendChild(msg);
    // Flash to page.
    document.getElementById('flash-alerts').appendChild(div);
    // Scroll to top of page.
    document.body.scrollTop = document.documentElement.scrollTop = 0;
}
