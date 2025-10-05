/**
 * Agam Organics - Main JavaScript
 * Client-side functionality and interactivity
 */

// Notification system
function showNotification(message, type = "info") {
  const notificationContainer =
    document.querySelector(".flash-messages") || createNotificationContainer();

  const notification = document.createElement("div");
  notification.className = `flash flash-${type}`;
  notification.innerHTML = `
        ${message}
        <button onclick="this.parentElement.remove()" class="flash-close">&times;</button>
    `;

  notificationContainer.appendChild(notification);

  // Auto remove after 5 seconds
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

function createNotificationContainer() {
  const container = document.createElement("div");
  container.className = "flash-messages";
  document.body.appendChild(container);
  return container;
}

// Smooth scroll to anchor
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Image lazy loading
if ("IntersectionObserver" in window) {
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.add("loaded");
        observer.unobserve(img);
      }
    });
  });

  document.querySelectorAll("img[data-src]").forEach((img) => {
    imageObserver.observe(img);
  });
}

// Form validation helpers
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function validatePhone(phone) {
  const re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
  return re.test(phone);
}

// Cart functionality
function updateCartCount() {
  fetch("/api/cart", {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const cartIcon = document.querySelector('.header-icon[href*="cart"]');
      if (cartIcon && data.total_items) {
        let badge = cartIcon.querySelector(".cart-badge");
        if (!badge) {
          badge = document.createElement("span");
          badge.className = "cart-badge";
          cartIcon.appendChild(badge);
        }
        badge.textContent = data.total_items;
      }
    })
    .catch((error) => console.error("Error updating cart count:", error));
}

// Initialize cart count on page load
if (document.querySelector('.header-icon[href*="cart"]')) {
  updateCartCount();
}

// Price formatter
function formatPrice(price) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 0,
  }).format(price);
}

// Date formatter
function formatDate(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-IN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(date);
}

// Debounce function for search
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Search functionality with debouncing
const searchInput = document.querySelector(".search-input");
if (searchInput) {
  searchInput.addEventListener(
    "input",
    debounce(function (e) {
      const query = e.target.value.trim();
      if (query.length >= 3) {
        // Perform search
        console.log("Searching for:", query);
      }
    }, 300)
  );
}

// Handle flash message auto-dismiss
document.addEventListener("DOMContentLoaded", function () {
  const flashMessages = document.querySelectorAll(".flash");
  flashMessages.forEach((flash) => {
    setTimeout(() => {
      flash.style.opacity = "0";
      setTimeout(() => flash.remove(), 300);
    }, 5000);
  });
});

// Prevent double form submission
const forms = document.querySelectorAll("form");
forms.forEach((form) => {
  form.addEventListener("submit", function (e) {
    const submitBtn = this.querySelector('button[type="submit"]');
    if (submitBtn && !submitBtn.disabled) {
      submitBtn.disabled = true;
      submitBtn.textContent = "Please wait...";

      // Re-enable after 3 seconds as fallback
      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.textContent =
          submitBtn.getAttribute("data-original-text") || "Submit";
      }, 3000);
    }
  });
});

// Store original button text
document.querySelectorAll('button[type="submit"]').forEach((btn) => {
  btn.setAttribute("data-original-text", btn.textContent);
});

// Handle network errors globally
window.addEventListener("online", () => {
  showNotification("Connection restored", "success");
});

window.addEventListener("offline", () => {
  showNotification("No internet connection", "warning");
});

// Handle unauthorized access
window.handleUnauthorized = function () {
  showNotification("Please login to continue", "warning");
  setTimeout(() => {
    window.location.href = "/login";
  }, 1500);
};

// Export functions for use in templates
window.showNotification = showNotification;
window.formatPrice = formatPrice;
window.formatDate = formatDate;
window.validateEmail = validateEmail;
window.validatePhone = validatePhone;
