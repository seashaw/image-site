/**
 * Sets up and initializes gallery.
 */
document.getElementById('links').onclick = function(event) {
    event = event || window.event;
    var target = event.target || event.srcElement,
            link = target.src ? target.parentNode : target,
            options = {index: link, event: event},
            links = this.getElementsByTagName('a');
    blueimp.Gallery(links, options);
};

/**
 * Add onclick event to 'reply' buttons.
 */
reply_buttons = document.getElementsByClassName('reply');
for (var i = 0; i < reply_buttons.length; i++) {
    reply_buttons[i].addEventListener("click", function(event) {
        // Prevent default link action.
        event.preventDefault();
        // Save reference to reply button.
        var reply_button = event.target;
        // Clear text content of comment form body.
        document.getElementById('body').value = null;
        // Set parent_id attribute of form to reply button name.
        // Name should be the id number of the comment.
        document.getElementById('parent_id').value = 
                reply_button.parentNode.parentNode.getAttribute('data-id');
        // Hide reply button.
        reply_button.classList.add('hide');
        // Show cancel button.
        document.getElementById('cancel').classList.remove('hide');
        // Move comment form into comment child section.
        reply_button.parentNode.parentNode.insertBefore(
                document.getElementById('comment-form'),
                reply_button.parentNode.parentNode.getElementsByClassName(
                        'panel')[0]); 
    }, false);
}

/**
 * Handle click event for comment 'cancel' button.
 */
document.getElementById('cancel').addEventListener("click", function(event) {
    // Prevent default link action.
    event.preventDefault();
    // Clear text of comment form body.
    document.getElementById('body').value = null;
    // Set parent_id of form to 0, indicating root level comment.
    document.getElementById('parent_id').value = 0;
    // Hide cancel button.
    event.target.classList.add('hide');
    // Show previously hidden reply button.
    document.getElementsByClassName('reply hide')[0].classList.remove('hide');
    // Move comment form into default comment section.
    document.getElementById('root-comment').appendChild(
            document.getElementById('comment-form'));

}, false);
