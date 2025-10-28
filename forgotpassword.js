function sendOTP() {
    let email = document.getElementById("email").value;
    if (email === "") {
        alert("Please enter your email.");
        return;
    }

    alert("OTP has been sent to " + email);
    document.getElementById("step1").style.display = "none";
    document.getElementById("step2").style.display = "block";
}

function verifyOTP() {
    let otp = document.getElementById("otp").value;
    if (otp === "1234") {  // You can replace this with actual OTP verification logic
        alert("OTP Verified!");
        document.getElementById("step2").style.display = "none";
        document.getElementById("step3").style.display = "block";
    } else {
        alert("Invalid OTP. Try again.");
    }
}

function resetPassword() {
    let newPassword = document.getElementById("new-password").value;
    let confirmPassword = document.getElementById("confirm-password").value;

    if (newPassword === "" || confirmPassword === "") {
        alert("Please fill all fields.");
        return;
    }

    if (newPassword !== confirmPassword) {
        alert("Passwords do not match.");
        return;
    }

    alert("Password reset successful! Redirecting to login...");
    window.location.href = "login.html";
}
