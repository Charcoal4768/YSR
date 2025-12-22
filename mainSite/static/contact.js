document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("quoteRequestForm");
    const submitbutton = document.querySelector(".bluebutton");
    const Addr1 = document.getElementById("addr1");
    const Addr2 = document.getElementById("addr2");
    const Phone = document.getElementById("phone");
    const Name = document.getElementById("name");
    const Email = document.getElementById("email");
    const Message = document.getElementById("msg");
    const CSRFToken = document.getElementById("csrf_token");
    const debug = false;
    function displaySuccessMessage() {
        // Create the message element
        const messageDiv = document.createElement('div');
        messageDiv.textContent = 'Sent Successfully!';

        // Apply inline CSS for styling and positioning
        messageDiv.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: #4CAF50;
            color: white;
            padding: 20px 40px;
            border-radius: 10px;
            font-size: 1.5rem;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
            pointer-events: none;
        `;

        document.body.appendChild(messageDiv);

        // Animate the fade-in
        setTimeout(() => {
            messageDiv.style.opacity = '1';
        }, 10);

        // Animate the fade-out and remove the element
        setTimeout(() => {
            messageDiv.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(messageDiv);
            }, 500); // Wait for fade-out to complete
        }, 3000); // Message stays for 3 seconds
    }
    function getLocalData() {
        const data = {
            address1: Addr1.value,
            address2: Addr2.value,
            recipient: Email.value,
            phone: Phone.value,
            name: Name.value,
            message: Message.value,
            csrf_token: CSRFToken.value
        };
        return data;
    }
    submitbutton.addEventListener("click", function (event) {
        event.preventDefault();
        submitbutton.disabled = true; // Disable the button to prevent multiple submissions
        const Data = getLocalData();
        if (debug) {
            console.log(Data);
            console.log(CSRFToken.value);
        }
        // Handle form submission
        fetch('/api/unauth_token', {
            method: 'GET',
            credentials: 'include'
        }).then(response => response.json())
            .then(tokenData => {
                if (tokenData.publish_token) {
                    if (debug){
                        console.log(tokenData.publish_token);
                    }
                    fetch('/api/send_email', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRF-Token': CSRFToken.value,
                            'Publish-Token': tokenData.publish_token
                        },
                        credentials: 'include',
                        body: JSON.stringify(Data)
                    }).then(response => response.json()).then(data => {
                        if (data.success) {
                            displaySuccessMessage();
                            submitbutton.disabled = false; // Re-enable the button
                            form.reset();
                        }
                    });
                }
            });
    });
});
