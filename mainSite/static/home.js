function getElementsByIDPrefix(prefix) {
    // Use a CSS attribute selector to find all elements where the 'id' attribute starts with the given prefix.
    const selector = `[id^="${prefix}"]`;
    // document.querySelectorAll returns a static NodeList containing all matching elements.
    return document.querySelectorAll(selector);
}

function AddSideBarLinks() {
    let test = getElementsByIDPrefix("cat-");
    let sideBarCategories = document.querySelector(".catalog-items");

    // Clear existing links before adding new ones
    sideBarCategories.innerHTML = '';

    test.forEach((element) => {
        let newLink = document.createElement("h3");
        newLink.innerText = element.innerText;
        newLink.addEventListener('click', () => {
            // Calculate the target scroll position
            const targetPosition = element.getBoundingClientRect().top + window.scrollY + 40;
            // Use window.scrollTo for smooth scrolling with the desired offset
            window.scrollTo({
                top: targetPosition,
                behavior: "smooth"
            });
        });
        sideBarCategories.appendChild(newLink);
        newLink.addEventListener('click', function() {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('visible');
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => { AddSideBarLinks() }, 100);
    let quoteButton = document.getElementById("Quote-button");
    quoteButton.addEventListener('click', (event) => {
        // prevent defaults
        event.preventDefault();
        const targetElement = document.getElementById("Quote-form");
        window.scrollTo({
            top: targetElement.getBoundingClientRect().top + window.scrollY - 40,
            behavior: "smooth"
        });
        if (!targetElement.classList.contains('visible')) {
            targetElement.classList.add('visible');
        }
        // Reset animation by removing + re-adding the class
        targetElement.classList.remove('border-glow-resize');
        void targetElement.offsetWidth; // force reflow
        targetElement.classList.add('border-glow-resize');
    });
});

window.addSideBarLinks = function () {
    AddSideBarLinks();
};