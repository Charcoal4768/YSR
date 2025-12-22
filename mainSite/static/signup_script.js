document.addEventListener("DOMContentLoaded", function() {
    const checkbox = document.getElementById("show-password");
    checkbox.addEventListener("click", function() {
        var passwordField = document.getElementById("password");
        var passwordField2 = document.getElementById("password2");
        if (checkbox.checked) {
            console.log("Checked");
            passwordField.setAttribute("type", "text");
            passwordField2.setAttribute("type", "text");
        } else {
            passwordField.setAttribute("type", "password");
            passwordField2.setAttribute("type", "password");
        }
    });
});

