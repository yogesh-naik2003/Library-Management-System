document.addEventListener("DOMContentLoaded", function () {
    const questions = document.querySelectorAll(".faq-question");

    questions.forEach((question) => {
        question.addEventListener("click", function () {
            const answer = this.nextElementSibling;
            const icon = this.querySelector(".toggle-icon");

            // Close all open answers before opening the new one
            document.querySelectorAll(".faq-answer").forEach((el) => {
                el.classList.remove("active");
                el.style.maxHeight = null;
            });

            document.querySelectorAll(".toggle-icon").forEach((el) => {
                el.textContent = "+";
                el.style.transform = "rotate(0deg)";
            });

            // Open the clicked answer if it was not already open
            if (!answer.classList.contains("active")) {
                answer.classList.add("active");
                answer.style.maxHeight = answer.scrollHeight + "px";
                icon.textContent = "-";
                icon.style.transform = "rotate(180deg)";
            }
        });
    });
});
