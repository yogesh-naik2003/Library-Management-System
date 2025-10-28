document.addEventListener('DOMContentLoaded', function () {
    const username = localStorage.getItem('username');
    if (!username) {
        // Not logged in, redirect to login or show public page
        window.location.href = 'loginstudent.html';
        return;
    }

    // Fetch and display only this student's data
    fetch(`/borrowed-books?username=${encodeURIComponent(username)}`)
        .then(res => res.json())
        .then(books => {
            // Render books for this student only
        });
});

// On logout button click
document.getElementById('logoutButton').addEventListener('click', function() {
    localStorage.removeItem('username');
    window.location.href = 'loginstudent.html';
});

function logout() {
    // Show the loader
    document.getElementById("loader-container").style.display = "flex";

    // Wait 3 seconds before redirecting
    setTimeout(() => {
        window.location.href = 'main.html';
    }, 3000);
}
