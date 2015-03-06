/**
 * Adds onclick event to image links and sets options for Gallery.
 */
document.getElementById('links').onclick = function(event) {
    event = event || window.event;
    var target = event.target || event.srcElement,
            link = target.src ? target.parentNode : target,
            options = {index: link, event: event},
            links = this.getElementsByTagName('a');
    blueimp.Gallery(links, options);
};

reply_buttons = document.getElementsByClassName('reply');
for (var i = 0; i < reply_buttons.length; i++) {
    reply_buttons[i].addEventListener("click", function(event) {
        event.preventDefault();
        document.getElementById('body').value = null;
        document.getElementById('parent_id').value = event.target.name;
        /*
        event.target.classList.toggle('hide');
        event.target.nextElementSibling.classList.toggle('hide');
        console.log(event.target.nextElementSibling.classList);
        */
        event.target.parentNode.insertBefore(
            document.getElementsByTagName('form')[0],
            event.target.nextElementSibling.nextElementSibling); 
    }, false);
}
cancel_buttons = document.getElementsByClassName('cancel');
for (var i = 0; i < cancel_buttons.length; i++) {
    cancel_buttons[i].addEventListener("click", function(event) {
        event.preventDefault();
        document.getElementById('body').value = null;
        document.getElementById('parent_id').value = event.target.name;
        /*
        event.target.classList.toggle('hide');
        event.target.previousElementSibling.classList.toggle('hide');
        console.log(event.target.previousElementSibling.classList);
        */
        document.getElementById('comment').appendChild(
            document.getElementsByTagName('form')[0]);

    }, false);
}
