var swiper = new Swiper(".swiper-index", {
  direction: "vertical",
  autoplay: {
    delay: 2500,
    disableOnInteraction: false,
  },
  slidesPerView: 1,
  spaceBetween: 30,
  mousewheel: true,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  
});
var swiper = new Swiper(".swiper-show", {
  effect: "cards",
  grabCursor: true,
  autoplay: {
    delay: 2500,
    disableOnInteraction: false,
  },
});

document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("projectForm");
  const checkboxes = form.querySelectorAll("input[type='checkbox']");
  const maxSelections = 5;

  checkboxes.forEach(function(checkbox) {
      checkbox.addEventListener("change", function() {
          const checkedCount = form.querySelectorAll("input[type='checkbox']:checked").length;
          if (checkedCount >= maxSelections) {
              checkboxes.forEach(function(cb) {
                  if (!cb.checked) {
                      cb.disabled = true;
                  }
              });
          } else {
              checkboxes.forEach(function(cb) {
                  cb.disabled = false;
              });
          }
      });
  });
});
var swiper = new Swiper(".swiper_project_image", {
  autoplay: {
    delay: 2500,
    disableOnInteraction: false,
  },
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    
    renderBullet: function (index, className) {
      return '<span class="' + className +'">' + (index + 1) + "</span>";
    },
  },
});