// Dashboard JavaScript

document.addEventListener("DOMContentLoaded", () => {
  // Sidebar toggle functionality
  const sidebarToggle = document.getElementById("sidebarToggle")
  const sidebar = document.getElementById("sidebar")
  const mainContent = document.getElementById("mainContent")

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed")
      mainContent.classList.toggle("expanded")

      // Store sidebar state in localStorage
      const isCollapsed = sidebar.classList.contains("collapsed")
      localStorage.setItem("sidebarCollapsed", isCollapsed)
    })
  }

  // Restore sidebar state from localStorage
  const sidebarCollapsed = localStorage.getItem("sidebarCollapsed")
  if (sidebarCollapsed === "true") {
    sidebar.classList.add("collapsed")
    mainContent.classList.add("expanded")
  }



  // Handle window resize
  window.addEventListener("resize", handleMobileSidebar)
  handleMobileSidebar() // Initial call
  
})
