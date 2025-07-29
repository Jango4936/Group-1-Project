

// live update when typing in search bar
document.addEventListener("DOMContentLoaded", () => {
  const input  = document.getElementById("searchInput");
  if (!input) return;                    // stops here if not found

  const getList = () => document.getElementById("appointmentsList");
  let timer;

  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      const url = new URL(window.location.href);
      url.searchParams.set("q", input.value);

      fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(r => r.text())
        .then(html => {
          const tmp = document.createElement("div");
          tmp.innerHTML = html;
          const fresh = tmp.querySelector("#appointmentsList");
          const old   = getList();
          if (fresh && old) old.replaceWith(fresh);
        })
        .catch(err => console.error("live-search error", err));
    }, 300);
  });
});