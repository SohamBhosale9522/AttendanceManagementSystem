// Main Application JavaScript

document.addEventListener('DOMContentLoaded', function () {
  // Toggle Sidebar on mobile
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebarBackdrop');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      if (backdrop) {
        backdrop.classList.toggle('show');
      }
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', function () {
      sidebar.classList.remove('show');
      backdrop.classList.remove('show');
    });
  }

  // Auto-dismiss alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });

  // Client-side quick filter for tables
  const clientFilterInput = document.getElementById('tableSearchInput');
  if (clientFilterInput) {
    clientFilterInput.addEventListener('keyup', function () {
      const filterValue = this.value.toLowerCase();
      const targetTable = document.querySelector(this.getAttribute('data-table-target') || 'table');
      if (targetTable) {
        const rows = targetTable.querySelectorAll('tbody tr');
        rows.forEach(function (row) {
          const rowText = row.textContent.toLowerCase();
          row.style.display = rowText.indexOf(filterValue) > -1 ? '' : 'none';
        });
      }
    });
  }
});
