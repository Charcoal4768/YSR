document.addEventListener("DOMContentLoaded", function() {
    const checkbox = document.getElementById("show-password");
    checkbox.addEventListener("click", function() {
        var passwordField = document.getElementById("password");
        if (checkbox.checked) {
            passwordField.setAttribute("type", "text");
        } else {
            passwordField.setAttribute("type", "password");
        }
    });
});
