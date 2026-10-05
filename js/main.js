/**
 * CampusHub - Core Application & Global UI Helpers
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initMobileMenu();
  setupGlobalModalTriggers();
});

/* ==========================================================================
   1. Toast Notification System
   ========================================================================== */
function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = {
    success: 'fa-solid fa-circle-check',
    danger: 'fa-solid fa-circle-exclamation',
    warning: 'fa-solid fa-triangle-exclamation',
    info: 'fa-solid fa-circle-info'
  };

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <i class="${icons[type] || icons.info} toast-icon"></i>
    <span class="toast-message">${escapeHtml(message)}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(50px)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ==========================================================================
   2. Navbar & Session Sync
   ========================================================================== */
function initNavbar() {
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });
  }

  // Update nav actions based on login state
  const navActions = document.getElementById('nav-actions-container');
  if (!navActions) return;

  const currentUser = auth.getCurrentUser();

  if (currentUser) {
    const isUserAdmin = currentUser.role === 'admin';
    const dashboardLink = isUserAdmin ? 'admin-dashboard.html' : 'student-dashboard.html';
    const dashboardLabel = isUserAdmin ? 'Admin Center' : 'My Dashboard';

    navActions.innerHTML = `
      <div class="nav-user-dropdown">
        <button type="button" class="user-profile-btn" id="user-dropdown-btn">
          <div class="avatar-circle">
            ${currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
          </div>
          <span style="max-width: 110px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(currentUser.name.split(' ')[0])}</span>
          <i class="fa-solid fa-chevron-down" style="font-size: 0.75rem;"></i>
        </button>
        <div class="dropdown-menu" id="user-dropdown-menu">
          <div class="dropdown-header">
            <div class="user-name">${escapeHtml(currentUser.name)}</div>
            <div class="user-role">${currentUser.role}</div>
          </div>
          <a href="${dashboardLink}" class="dropdown-item">
            <i class="fa-solid fa-chart-pie"></i> ${dashboardLabel}
          </a>
          ${!isUserAdmin ? `
            <a href="my-events.html" class="dropdown-item">
              <i class="fa-solid fa-ticket"></i> My Registered Events
            </a>
          ` : `
            <a href="admin-events.html" class="dropdown-item">
              <i class="fa-solid fa-calendar-plus"></i> Manage Events
            </a>
            <a href="admin-registrations.html" class="dropdown-item">
              <i class="fa-solid fa-users"></i> Registrations
            </a>
          `}
          <a href="profile.html" class="dropdown-item">
            <i class="fa-solid fa-user-gear"></i> Profile Settings
          </a>
          <div class="dropdown-divider"></div>
          <button type="button" class="dropdown-item text-danger" id="nav-logout-btn" style="color: var(--danger-500); width: 100%;">
            <i class="fa-solid fa-arrow-right-from-bracket"></i> Sign Out
          </button>
        </div>
      </div>
    `;

    // Dropdown toggle
    const dropdownBtn = document.getElementById('user-dropdown-btn');
    const dropdownMenu = document.getElementById('user-dropdown-menu');
    if (dropdownBtn && dropdownMenu) {
      dropdownBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle('show');
      });

      document.addEventListener('click', () => {
        dropdownMenu.classList.remove('show');
      });
    }

    // Logout trigger
    const logoutBtn = document.getElementById('nav-logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        auth.logout();
      });
    }
  } else {
    navActions.innerHTML = `
      <a href="login.html" class="btn btn-secondary btn-sm">Log In</a>
      <a href="register.html" class="btn btn-primary btn-sm btn-desktop-only">Sign Up</a>
    `;
  }
}

/* ==========================================================================
   3. Mobile Navigation Drawer
   ========================================================================== */
function initMobileMenu() {
  const toggleBtn = document.getElementById('mobile-toggle-btn');
  const drawer = document.getElementById('mobile-drawer');
  const closeBtn = document.getElementById('drawer-close-btn');

  if (!drawer) return;

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      drawer.classList.add('open');
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      drawer.classList.remove('open');
    });
  }

  drawer.addEventListener('click', (e) => {
    if (e.target === drawer) {
      drawer.classList.remove('open');
    }
  });
}

/* ==========================================================================
   4. Modal Helper System
   ========================================================================== */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';
  }
}

function setupGlobalModalTriggers() {
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal(modal.id);
      }
    });

    modal.querySelectorAll('.modal-close, [data-modal-close]').forEach(btn => {
      btn.addEventListener('click', () => {
        closeModal(modal.id);
      });
    });
  });
}

/* ==========================================================================
   5. Helper Utilities & Formatters
   ========================================================================== */
function formatDate(dateString) {
  if (!dateString) return 'TBA';
  const d = new Date(dateString);
  if (isNaN(d.getTime())) return dateString;
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

function formatPrice(price) {
  const num = parseFloat(price);
  if (isNaN(num) || num === 0) return 'Free';
  return `$${num.toFixed(2)}`;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
