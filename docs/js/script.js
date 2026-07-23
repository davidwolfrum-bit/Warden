/**
 * script.js — scroll reveal, sticky header state, magnetic buttons.
 * No dependencies. Respects prefers-reduced-motion throughout.
 */
(function () {
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  /* ---------- Sticky header state ---------- */
  const header = document.getElementById("site-header");
  if (header) {
    const onScroll = () => {
      header.classList.toggle("scrolled", window.scrollY > 24);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- Scroll reveal ---------- */
  const revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length) {
    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      revealEls.forEach((el) => el.classList.add("is-visible"));
    } else {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
      );
      revealEls.forEach((el) => observer.observe(el));
    }
  }

  /* ---------- Magnetic buttons ---------- */
  if (!prefersReducedMotion) {
    document.querySelectorAll(".magnetic").forEach((btn) => {
      const strength = 12;

      btn.addEventListener("mousemove", (e) => {
        const rect = btn.getBoundingClientRect();
        const relX = (e.clientX - rect.left) / rect.width - 0.5;
        const relY = (e.clientY - rect.top) / rect.height - 0.5;
        btn.style.setProperty("--mx", `${relX * strength}px`);
        btn.style.setProperty("--my", `${relY * strength}px`);
      });

      btn.addEventListener("mouseleave", () => {
        btn.style.setProperty("--mx", "0px");
        btn.style.setProperty("--my", "0px");
      });
    });
  }
})();
