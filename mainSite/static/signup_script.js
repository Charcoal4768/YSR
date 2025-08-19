document.addEventListener("DOMContentLoaded", function() {
    // Your code to run when the DOM is fully loaded
    document.getElementById("show-password").addEventListener("click", function() {
        var passwordField = document.getElementById("password");
        var passwordField2 = document.getElementById("password2");
        if (this.checked) {
            passwordField.setAttribute("type", "text");
            passwordField2.setAttribute("type", "text");
        } else {
            passwordField.setAttribute("type", "password");
            passwordField2.setAttribute("type", "password");
        }
    });
});
