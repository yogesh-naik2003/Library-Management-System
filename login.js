document.addEventListener("DOMContentLoaded", function () {
    console.log("JS file loaded successfully!");

    // Student Login
    const studentSigninBtn = document.querySelector(".student-signin");
    if (studentSigninBtn) {
        studentSigninBtn.addEventListener("click", async function (event) {
            event.preventDefault(); // Prevent default form submission
            const username = document.querySelector(".student-username").value.trim();
            const password = document.querySelector(".student-password").value.trim();
            const role = "student";

            if (!username || !password) {
                showPopup("Please fill in all fields.", false);
                return;
            }

            try {
                const response = await fetch("http://127.0.0.1:5000/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ username, password, role }),
                });

                const result = await response.json();

                if (result.success) {
                    localStorage.setItem('username', username); // Save logged-in student
                    showPopup(result.message, true, function() {
                        window.location.href = "student-dashboard.html"; // Redirect to student dashboard
                    });
                } else {
                    showPopup(result.message, false);
                }
            } catch (error) {
                console.error("Error:", error);
                showPopup("An error occurred during login.", false);
            }
        });
    }

    // Admin Login
    const adminSigninBtn = document.querySelector(".admin-signin");
    if (adminSigninBtn) {
        adminSigninBtn.addEventListener("click", async function (event) {
            event.preventDefault(); // Prevent default form submission
            const username = document.querySelector(".admin-username").value.trim();
            const password = document.querySelector(".admin-password").value.trim();
            const role = "admin";

            if (!username || !password) {
                showPopup("Please fill in all fields.", false);
                return;
            }

            try {
                const response = await fetch("http://127.0.0.1:5000/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ username, password, role }),
                });

                const result = await response.json();

                if (result.success) {
                    showPopup(result.message, true, function() {
                        window.location.href = "admin-dashboard.html"; // Redirect to admin dashboard
                    });
                } else {
                    showPopup(result.message, false);
                }
            } catch (error) {
                console.error("Error:", error);
                showPopup("An error occurred during login.", false);
            }
        });
    }
});

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
  
    try {
      const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password, role }),
      });
  
      const result = await response.json();
  
      if (result.success) {
        // Store the token in localStorage
        localStorage.setItem('token', result.token);
        localStorage.setItem('username', username); // Save logged-in user
        showPopup(result.message, true, function() {
            window.location.href = role === 'admin' ? 'admin-dashboard.html' : 'student-dashboard.html'; // Redirect based on role
        });
      } else {
        showPopup(result.message, false);
      }
    } catch (error) {
      console.error('Error logging in:', error);
      showPopup('An error occurred. Please try again.', false);
    }
}

// Example: On logout (student)
function studentLogout() {
    localStorage.removeItem('username');
    window.location.href = 'loginstudent.html'; // Redirect to login page
}