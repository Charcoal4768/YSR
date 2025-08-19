document.addEventListener("DOMContentLoaded", function() {
    // Your code to run when the DOM is fully loaded
    document.getElementById("show-password").addEventListener("click", function() {
        var passwordField = document.getElementById("password");
        if (this.checked) {
            passwordField.setAttribute("type", "text");
        } else {
            passwordField.setAttribute("type", "password");
        }
    });
});
