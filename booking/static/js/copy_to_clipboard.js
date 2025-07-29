



document.addEventListener("DOMContentLoaded", () => {
  document.addEventListener("click", event => {
    // look for the closest button with either class
    const phoneBtn  = event.target.closest(".copy-btn");
    const emailBtn  = event.target.closest(".copyemail-btn");

    if (phoneBtn) {
      const phone = phoneBtn.dataset.phone;
      navigator.clipboard.writeText(phone)
        .then(() => alert(`Phone Number Copied: ${phone}`))
        .catch(() => alert("Could not copy the number."));
    }

    if (emailBtn) {
      const email = emailBtn.dataset.email;
      navigator.clipboard.writeText(email)
        .then(() => alert(`Email Copied: ${email}`))
        .catch(() => alert("Could not copy the email."));
    }
  });
});