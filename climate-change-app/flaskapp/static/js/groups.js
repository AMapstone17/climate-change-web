document.addEventListener("DOMContentLoaded", (event) => {
    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the button that opens the modal
    var btn = document.getElementById("post__delete-btn");

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
        var groupId = btn.getAttribute('data-group-id');
        if (groupId) {
            window.location.href = `/groups/delete_group/${groupId}`;
            modal.style.display = "none";
        } else {
            alert("Group ID not found!");
        }
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
