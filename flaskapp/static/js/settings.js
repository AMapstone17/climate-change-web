document.addEventListener('DOMContentLoaded', (event) => {
    // Function to hide all content divs
    function hideAllContent() {
        document.querySelectorAll('.content').forEach((contentDiv) => {
            contentDiv.style.display = 'none';
        });
    }

    // Function to remove the active class from all options
    function removeActiveClass() {
        document.querySelectorAll('.selection-option').forEach((option) => {
            option.classList.remove('active-option');
        });
    }

    // Function to show the content related to the clicked option and highlight it
    function showContent(contentId, optionElement) {
        hideAllContent();
        removeActiveClass();
        document.getElementById(contentId).style.display = 'block';
        optionElement.classList.add('active-option');
        // Save the active content ID to localStorage
        localStorage.setItem('activeContentId', contentId);
    }

    // Event listeners for the selection options
    document.getElementById('change-password-option').addEventListener('click', function () {
        showContent('change-password-content', this);
    });
    document.getElementById('change-info-option').addEventListener('click', function () {
        showContent('change-info-content', this);
    });
    document.getElementById('create-admin-option').addEventListener('click', function () {
        showContent('create-admin-content', this);
    });
    document.getElementById('view-users-option').addEventListener('click', function () {
        showContent('view-users-content', this);
    });

    // Check if there's an active content ID saved in localStorage
    const activeContentId = localStorage.getItem('activeContentId');
    if (activeContentId) {
        const activeOptionElement = document.querySelector(`#${activeContentId.replace('-content', '-option')}`);
        if (activeOptionElement) {
            showContent(activeContentId, activeOptionElement);
        }
    } else {
        // If no active content ID, default to first option
        showContent('change-password-content', document.getElementById('change-password-option'));
    }


// Get the modal
    var modal = document.getElementById("myModal");

// Get the button that opens the modal
    var btn = document.getElementById("delete-btn");

// Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

// Get the Yes button
    var yesBtn = document.getElementById("yes-btn");

// Get the No button
    var noBtn = document.getElementById("no-btn");

// When the user clicks the button, open the modal
    btn.onclick = function () {
        modal.style.display = "block";
    }

// When the user clicks on <span> (x), close the modal
    span.onclick = function () {
        modal.style.display = "none";
    }

// When the user clicks on Yes button, delete the account
    yesBtn.onclick = function () {
        window.location.href = '/account/delete';
        modal.style.display = "none";
        alert("Account deleted successfully!");
    }

// When the user clicks on No button, close the modal
    noBtn.onclick = function () {
        modal.style.display = "none";
    }

// When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

});
