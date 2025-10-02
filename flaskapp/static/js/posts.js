window.onload = function () {
    var shortDescription = document.querySelector('.short-description');
    var text = shortDescription.innerText;
    var lineHeight = parseInt(window.getComputedStyle(shortDescription)['line-height']);
    var height = shortDescription.offsetHeight;

    var lines = Math.floor(height / lineHeight);
    if (lines > 3) {
        var words = text.split(' ');
        while (lines > 3) {
            words.pop();
            shortDescription.innerText = words.join(' ') + '...';
            height = shortDescription.offsetHeight;
            lines = Math.floor(height / lineHeight);
        }
    }
    // Hide all post displays initially
    var displays = document.querySelectorAll('.short-post-display');
    for (var i = 0; i < displays.length; i++) {
        displays[i].style.display = 'none';
    }


    // Show 'all-posts-display' by default
    var allPostsDisplay = document.getElementById('all-posts-display');
    allPostsDisplay.style.display = 'block';

    var allPostsButton = document.getElementById('all-posts');
    allPostsButton.style.backgroundColor = 'gray';

    // Function to handle button click
    function handleClick(buttonId, displayId) {
        var button = document.getElementById(buttonId);
        button.addEventListener('click', function () {
            // Hide all post displays
            for (var i = 0; i < displays.length; i++) {
                displays[i].style.display = 'none';
            }

            // Remove active background color from all buttons
            var buttons = document.querySelectorAll('.btn');
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].style.backgroundColor = '';
            }

            // Show corresponding display and set active background color
            var display = document.getElementById(displayId);
            display.style.display = 'block';
            buttons.style.backgroundColor = 'gray';
        });
    }

    // Attach event listeners to buttons
    handleClick('my-posts', 'my-posts-display');
    handleClick('all-posts', 'all-posts-display');
    handleClick('digests', 'digests-display');
}
