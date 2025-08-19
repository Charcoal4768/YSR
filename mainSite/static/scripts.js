document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    const contactForm = document.querySelector('.contactForm');
    if (contactForm) {
      contactForm.classList.add('visible');
    }
  }, 3000);
  const burger = document.querySelector('.burger');
  burger.addEventListener('click', function() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('visible');
  });
});

// A simple throttle function to limit how often a function can run.
function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Function to check scroll position
const checkScroll = () => {
  const scrollPosition = window.scrollY || document.documentElement.scrollTop;
  const element = document.querySelector('nav');

  if (scrollPosition > 50) {
    // User has scrolled more than 200px
    // Do something, for example, add a class
    if (element && !element.classList.contains('scrolled')) {
      element.classList.add('scrolled');
      console.log('Scrolled past 200px');
    }
  } else {
    // User is within 200px of the top
    // Do something else, for example, remove a class
    if (element && element.classList.contains('scrolled')) {
      element.classList.remove('scrolled');
      console.log('Scrolled within 200px');
    }
  }
};

// Add the throttled scroll event listener
window.addEventListener('scroll', throttle(checkScroll, 10)); // The function will run at most once every 100ms