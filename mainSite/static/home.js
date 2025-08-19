function getElementsByIDPrefix(prefix) {
  // Use a CSS attribute selector to find all elements where the 'id' attribute starts with the given prefix.
  const selector = `[id^="${prefix}"]`;
  
  // document.querySelectorAll returns a static NodeList containing all matching elements.
  return document.querySelectorAll(selector);
}
