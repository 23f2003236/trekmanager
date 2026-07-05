/* ==========================================================================
   TrekVault — UI enhancement scripts.
   IMPORTANT: These are progressive enhancements only. Every core feature
   (navigation, forms, booking, filtering) works fully without JavaScript.
   ========================================================================== */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    initSidebar();
    initFlashes();
    initConfirms();
    initPasswordToggles();
  });

  /* --- Mobile sidebar drawer ------------------------------------------- */
  function initSidebar() {
    var shell = document.querySelector(".app-shell");
    if (!shell) return;

    document.querySelectorAll("[data-sidebar-open]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        shell.classList.add("sidebar-open");
      });
    });
    document.querySelectorAll("[data-sidebar-close]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        shell.classList.remove("sidebar-open");
      });
    });
    // Close drawer on Escape.
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") shell.classList.remove("sidebar-open");
    });
  }

  /* --- Auto-dismissing flash toasts ------------------------------------ */
  function initFlashes() {
    document.querySelectorAll(".flash-toast").forEach(function (toast) {
      var dismiss = function () {
        toast.style.transition = "opacity .3s, transform .3s";
        toast.style.opacity = "0";
        toast.style.transform = "translateX(120%)";
        setTimeout(function () { toast.remove(); }, 320);
      };
      var closeBtn = toast.querySelector("[data-flash-dismiss]");
      if (closeBtn) closeBtn.addEventListener("click", dismiss);
      // Auto dismiss after 5 seconds.
      setTimeout(dismiss, 5000);
    });
  }

  /* --- Confirm dialogs on destructive forms ---------------------------- */
  function initConfirms() {
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        if (!window.confirm(form.getAttribute("data-confirm"))) {
          e.preventDefault();
        }
      });
    });
  }

  /* --- Show / hide password fields ------------------------------------- */
  function initPasswordToggles() {
    document.querySelectorAll("[data-toggle-password]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var field = document.getElementById(btn.getAttribute("data-toggle-password"));
        if (!field) return;
        var icon = btn.querySelector("i");
        if (field.type === "password") {
          field.type = "text";
          if (icon) icon.className = "bi bi-eye-slash";
        } else {
          field.type = "password";
          if (icon) icon.className = "bi bi-eye";
        }
      });
    });
  }
})();
