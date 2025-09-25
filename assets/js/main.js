// Navigation Toggle
const navToggle = document.querySelector(".nav-toggle");
const navMenu = document.querySelector(".nav-menu");
const navLinks = document.querySelectorAll(".nav-menu a");

navToggle.addEventListener("click", () => {
  navToggle.classList.toggle("active");
  navMenu.classList.toggle("active");
  document.body.style.overflow = navMenu.classList.contains("active")
    ? "hidden"
    : "auto";
});

// Also close menu when clicking on the overlay
navMenu.addEventListener("click", (e) => {
  if (e.target === navMenu) {
    navToggle.classList.remove("active");
    navMenu.classList.remove("active");
    document.body.style.overflow = "auto";
  }
});

// Close menu with Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && navMenu.classList.contains("active")) {
    navToggle.classList.remove("active");
    navMenu.classList.remove("active");
    document.body.style.overflow = "auto";
  }
});

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    navToggle.classList.remove("active");
    navMenu.classList.remove("active");
    document.body.style.overflow = "auto";
  });
});

// Section Animation on Scroll
const sections = document.querySelectorAll(".section");

const checkSectionVisibility = () => {
  sections.forEach((section) => {
    const sectionTop = section.getBoundingClientRect().top;
    const windowHeight = window.innerHeight;

    if (sectionTop < windowHeight * 0.85) {
      section.classList.add("active");
    }
  });
};

window.addEventListener("scroll", checkSectionVisibility);
window.addEventListener("load", checkSectionVisibility);

// Page-specific functionality
if (document.body.classList.contains("home")) {
  // Home page - no scroll functionality needed
  console.log("Home page loaded");
} else {
  // Other pages - smooth scroll to top functionality
  window.addEventListener("load", () => {
    window.scrollTo(0, 0);
  });
}

// Back to Top Button Functionality
const backToTopButton = document.getElementById("backToTop");

// Show/hide back to top button based on scroll position
window.addEventListener("scroll", () => {
  if (window.pageYOffset > 300) {
    backToTopButton.classList.add("visible");
  } else {
    backToTopButton.classList.remove("visible");
  }
});

// Smooth scroll to top when button is clicked
backToTopButton.addEventListener("click", () => {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
});

// Contact Form Functionality
const contactForm = document.getElementById("contactForm");

if (contactForm) {
  contactForm.addEventListener("submit", function (e) {
    e.preventDefault();

    // Get form data
    const formData = new FormData(contactForm);
    const formObject = {};

    // Convert FormData to object
    for (let [key, value] of formData.entries()) {
      formObject[key] = value;
    }

    // Basic validation
    if (!formObject.name || !formObject.email || !formObject.message) {
      alert("Please fill in all required fields.");
      return;
    }

    // Send form data to email service
    const submitBtn = contactForm.querySelector(".submit-btn");
    const originalText = submitBtn.innerHTML;

    // Show loading state
    submitBtn.innerHTML = "<span>Sending...</span>";
    submitBtn.disabled = true;

    // Option 1: Using Formspree (replace YOUR_FORM_ID with actual Formspree form ID)
    fetch("https://formspree.io/f/YOUR_FORM_ID", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formObject),
    })
      .then((response) => {
        if (response.ok) {
          showSuccessDialog(formObject.name);
          contactForm.reset();
        } else {
          alert(
            "Sorry, there was an error sending your message. Please try again."
          );
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert(
          "Sorry, there was an error sending your message. Please try again."
        );
      })
      .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
      });

    // Option 2: For testing - just log the data (remove this in production)
    console.log("Form data that would be sent:", formObject);
  });
}

// Custom Dialog Functions
function showSuccessDialog(userName) {
  // Create dialog HTML
  const dialogHTML = `
    <div class="dialog-overlay" id="successDialog">
      <div class="dialog-box">
        <button class="dialog-close" onclick="closeSuccessDialog()">&times;</button>
        <div class="dialog-content">
          <h3 class="dialog-title">Thank you <span class="dialog-name">${userName}</span>!</h3>
          <p class="dialog-message">We'll reach out to you shortly!</p>
        </div>
      </div>
    </div>
  `;

  // Add dialog to body
  document.body.insertAdjacentHTML("beforeend", dialogHTML);

  // Show dialog with animation
  setTimeout(() => {
    document.getElementById("successDialog").classList.add("active");
  }, 10);

  // Close dialog when clicking overlay
  document
    .getElementById("successDialog")
    .addEventListener("click", function (e) {
      if (e.target === this) {
        closeSuccessDialog();
      }
    });
}

function closeSuccessDialog() {
  const dialog = document.getElementById("successDialog");
  if (dialog) {
    dialog.classList.remove("active");
    setTimeout(() => {
      dialog.remove();
    }, 300);
  }
}

// Mobile Optimizations
document.addEventListener("DOMContentLoaded", function () {
  // Prevent zoom on iOS when focusing inputs
  const inputs = document.querySelectorAll("input, select, textarea");
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      if (window.innerWidth <= 768) {
        document
          .querySelector("meta[name=viewport]")
          .setAttribute(
            "content",
            "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
          );
      }
    });

    input.addEventListener("blur", function () {
      if (window.innerWidth <= 768) {
        document
          .querySelector("meta[name=viewport]")
          .setAttribute(
            "content",
            "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
          );
      }
    });
  });

  // Improve touch scrolling on mobile
  if ("ontouchstart" in window) {
    document.body.style.webkitOverflowScrolling = "touch";
  }

  // Optimize navigation for mobile
  const navMenu = document.querySelector(".nav-menu");
  if (navMenu) {
    // Prevent body scroll when menu is open on mobile
    navMenu.addEventListener(
      "touchmove",
      function (e) {
        if (navMenu.classList.contains("active")) {
          e.preventDefault();
        }
      },
      { passive: false }
    );
  }

  // Mobile-specific gallery optimizations
  const galleryItems = document.querySelectorAll(".gallery-item");
  if (window.innerWidth <= 768) {
    galleryItems.forEach((item) => {
      // Add touch feedback and ensure images load properly
      const img = item.querySelector('img');
      if (img) {
        // Ensure images are loaded
        if (!img.complete) {
          img.addEventListener('load', function() {
            this.style.opacity = '1';
          });
        }
        
        // Add touch feedback
        item.addEventListener("touchstart", function () {
          this.style.transform = 'scale(0.98)';
          this.style.opacity = "0.8";
        });

        item.addEventListener("touchend", function () {
          this.style.transform = 'scale(1)';
          this.style.opacity = "1";
        });
      }
    });
  }

  // Optimize video for mobile
  const video = document.getElementById("video-background");
  if (video) {
    if (window.innerWidth <= 768) {
      // On mobile, optimize video settings
      video.setAttribute('preload', 'metadata');
      video.muted = true;
      video.playsInline = true;
      
      // Add a play button overlay for mobile users to choose
      const playButton = document.createElement('div');
      playButton.innerHTML = '▶️ Tap to play background video';
      playButton.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 15px 25px;
        border-radius: 25px;
        cursor: pointer;
        z-index: 2;
        font-size: 14px;
        border: 1px solid rgba(255,255,255,0.3);
      `;
      
      const mainContent = document.querySelector('.main-content');
      if (mainContent) {
        mainContent.appendChild(playButton);
        
        playButton.addEventListener('click', function() {
          video.play();
          playButton.style.display = 'none';
        });
      }
    } else {
      // On desktop, auto-play as normal
      video.play().catch(e => console.log('Video autoplay prevented:', e));
    }
  }
});

// Handle orientation changes
window.addEventListener("orientationchange", function () {
  // Refresh layout after orientation change
  setTimeout(function () {
    window.scrollTo(0, 0);

    // Recalculate heights if needed
    const sections = document.querySelectorAll(".section");
    sections.forEach((section) => {
      section.style.minHeight = window.innerHeight + "px";
    });
  }, 100);
});

// Optimize scroll performance on mobile
let ticking = false;
function updateScrollElements() {
  // Your scroll-based animations here
  ticking = false;
}

window.addEventListener("scroll", function () {
  if (!ticking) {
    requestAnimationFrame(updateScrollElements);
    ticking = true;
  }
});
