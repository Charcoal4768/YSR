function getElementsByIDPrefix(prefix) {
  // Use a CSS attribute selector to find all elements where the 'id' attribute starts with the given prefix.
  const selector = `[id^="${prefix}"]`;
  
  // document.querySelectorAll returns a static NodeList containing all matching elements.
  return document.querySelectorAll(selector);
}

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    let test = getElementsByIDPrefix("cat-");
    let sideBarCategories = document.querySelector(".catalog-items");
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
    });
  }, 100);
});