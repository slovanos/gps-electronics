// Builds the contact e-mail links from data attributes (anti-spam).
document.querySelectorAll(".contact-mail").forEach((a) => {
  const mail = `${a.dataset.user}@${a.dataset.domain}`;
  a.href = `mailto:${mail}`;
  a.textContent = mail;
});

// Mobile menu: the button opens and closes it; choosing a link closes it.
const header = document.querySelector(".site-header");
const toggle = header.querySelector(".menu-toggle");
const setOpen = (open) => {
  header.classList.toggle("menu-open", open);
  toggle.setAttribute("aria-expanded", open);
};
toggle.addEventListener("click", () => setOpen(!header.classList.contains("menu-open")));
header.querySelectorAll(".site-nav a").forEach((a) => a.addEventListener("click", () => setOpen(false)));
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && header.classList.contains("menu-open")) {
    setOpen(false);
    toggle.focus();
  }
});
