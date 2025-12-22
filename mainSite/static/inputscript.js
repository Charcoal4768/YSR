document.addEventListener("DOMContentLoaded", () => {
    // Selects all 'p' tags that are a direct child of a 'div'
    // with the class 'material-input' and have the 'contenteditable' attribute.
    const editableMaterialPs = document.querySelectorAll("div.material-input > p[contenteditable]");

    // Check each of the fetched p tags.
    editableMaterialPs.forEach(pTag => {
        pTag.addEventListener("input", () => {
            // Trim the content to check if it's truly empty, ignoring whitespace.
            const content = pTag.textContent.trim();
            // If the content is not an empty string, add the '.filled' class
            // to the p tag's parent element.
            if (content !== "") {
                pTag.parentElement.classList.add("filled");
            } else{
                pTag.parentElement.classList.remove("filled");
            }
        });
        pTag.addEventListener("keydown", (event) => {
            // Check if the pressed key is the Enter key
            if (event.key === "Enter") {
                // Prevent the default behavior (creating a new line)
                event.preventDefault();
            }
        });
    });
});
