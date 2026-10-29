// Builds the contact e-mail link from data attributes (anti-spam).
document.querySelectorAll(".contact-mail").forEach((a) => {
  const mail = `${a.dataset.user}@${a.dataset.domain}`;
  a.href = `mailto:${mail}`;
  a.textContent = mail;
});
