function pushFooter() {
    var footer = document.getElementById('footer');
    var pusher = document.getElementById('pusher');
    pusher.style.height = "0px";
    var page_height = document.body.offsetHeight;
    if (page_height < window.innerHeight) {
        var diff = (window.innerHeight - page_height);
        // This part could use some tweaking.
        diff -= footer.offsetHeight * 2 - 3;
        pusher.style.height = diff.toString() + "px";
    }
}

// Positions footer on page load.
pushFooter();

// Repositions footer on window resize.
window.onresize = pushFooter;
