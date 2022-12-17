const mobileIcon = document.querySelector(".mobile-menu-icon");
const menu = document.querySelector(".nav-links");

mobileIcon.addEventListener("click", handelMobileMenu);

function handelMobileMenu() {
  console.log("klikanie działa");
  menu.classList.toggle("opened");
}