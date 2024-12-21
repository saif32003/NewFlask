
window.addEventListener('load', function() {
  setTimeout(function() {
      document.body.classList.add('loaded'); // Add 'loaded' class to hide preloader
  }, 4000); // 4 seconds delay
});
// Attach click event listeners to the buttons
scrollLeftBtn.addEventListener('click', scrollLeft);
scrollRightBtn.addEventListener('click', scrollRight);

 // Attach event listeners to buttons
 scrollLeftBtn.addEventListener('click', scrollLeft);
 scrollRightBtn.addEventListener('click', scrollRight);
function toggleMenu() {
    const links = document.querySelector('.navbar-links');
    links.classList.toggle('active');  // Toggle the 'active' class to show/hide the menu
}
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
var video = document.getElementById("myVideo");
video.playbackRate = 10; // 1.5 times faster than normal speed

// Function to handle scroll-based animations
document.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('.who-are-we-section');
    
    sections.forEach(section => {
        const sectionPosition = section.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;

        if (sectionPosition < screenPosition) {
            section.classList.add('animated');
        }
    });
});



