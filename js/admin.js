/**
 * CampusHub - Admin Portal Controller (Dashboard, Events CRUD, Registrations)
 */

let adminEventsCache = [];
let adminRegistrationsCache = [];
let selectedEventForEdit = null;

/* ==========================================================================
   1. Admin Dashboard Overview (admin-dashboard.html)
   ========================================================================== */
async function initAdminDashboard() {
  auth.requireAdmin();

  const user = auth.getCurrentUser();
  const nameEl = document.getElementById('admin-greeting-name');
  if (nameEl) nameEl.textContent = user.name;

  try {
    const stats = await api.getStats();
    
    // Update metric cards
    document.getElementById('stat-total-events').textContent = stats.totalEvents;
    document.getElementById('stat-total-registrations').textContent = stats.totalRegistrations;
    document.getElementById('stat-total-students').textContent = stats.totalStudents;
    document.getElementById('stat-fill-rate').textContent = `${stats.fillRate}%`;

    // Load recent registrations
    const recentRegs = await api.getRegistrations();
    const tbody = document.getElementById('admin-recent-regs-tbody');
    if (tbody) {
      if (recentRegs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--slate-500); padding: 2rem;">No registrations recorded yet.</td></tr>`;
      } else {
        tbody.innerHTML = recentRegs.slice(0, 5).map(reg => `
          <tr>
            <td>
              <strong>${escapeHtml(reg.userName)}</strong><br/>
              <span style="font-size: 0.775rem; color: var(--slate-500);">${escapeHtml(reg.userEmail)}</span>
            </td>
            <td>${escapeHtml(reg.eventTitle)}</td>
            <td><code>${escapeHtml(reg.ticketCode)}</code></td>
            <td>${formatDate(reg.registeredAt)}</td>
            <td>
              <span class="badge ${reg.attended ? 'badge-success' : 'badge-secondary'}">
                ${reg.attended ? 'Attended' : 'Registered'}
              </span>
            </td>
          </tr>
        `).join('');
      }
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

/* ==========================================================================
   2. Admin Events Management & CRUD (admin-events.html)
   ========================================================================== */
async function initAdminEvents() {
  auth.requireAdmin();
  try {
    adminEventsCache = await api.getEvents();
    renderAdminEventsTable(adminEventsCache);
    setupAdminEventsFilter();
    setupEventFormHandlers();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderAdminEventsTable(events) {
  const tbody = document.getElementById('admin-events-tbody');
  if (!tbody) return;

  if (events.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 3rem; color: var(--slate-500);">
          <i class="fa-solid fa-calendar-xmark" style="font-size: 2rem; margin-bottom: 0.5rem; display: block; color: var(--slate-300);"></i>
          No events found. Click "+ Create Event" to add a new event.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = events.map(evt => {
    const isFull = evt.registeredCount >= evt.capacity;
    return `
      <tr>
        <td>
          <div class="table-event-cell">
            <img src="${escapeHtml(evt.image)}" class="table-event-thumb" alt="" />
            <div class="table-event-info">
              <span class="table-event-title">${escapeHtml(evt.title)}</span>
              <span class="table-event-date">${escapeHtml(evt.venue)}</span>
            </div>
          </div>
        </td>
        <td>
          <span class="badge badge-${evt.category.toLowerCase()}">${escapeHtml(evt.category)}</span>
        </td>
        <td>${formatDate(evt.date)}</td>
        <td>
          <strong>${evt.registeredCount}</strong> / ${evt.capacity}
          <div style="font-size: 0.75rem; color: ${isFull ? 'var(--danger-500)' : 'var(--slate-500)'};">
            ${isFull ? 'At Capacity' : `${evt.capacity - evt.registeredCount} left`}
          </div>
        </td>
        <td>${formatPrice(evt.price)}</td>
        <td>
          <span class="badge ${evt.status === 'Published' ? 'badge-success' : 'badge-warning'}">
            ${evt.status}
          </span>
        </td>
        <td style="text-align: right;">
          <div style="display: inline-flex; gap: 0.4rem;">
            <a href="event-details.html?id=${encodeURIComponent(evt.id)}" class="btn btn-secondary btn-sm" title="Preview Event">
              <i class="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
            <button type="button" class="btn btn-secondary btn-sm" onclick="openEditEventModal('${evt.id}')" title="Edit Event">
              <i class="fa-solid fa-pen-to-square"></i>
            </button>
            <button type="button" class="btn btn-danger-outline btn-sm" onclick="handleDeleteEvent('${evt.id}')" title="Delete Event">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function setupAdminEventsFilter() {
  const searchInput = document.getElementById('admin-event-search');
  const catFilter = document.getElementById('admin-event-category-filter');

  function applyFilter() {
    const q = searchInput ? searchInput.value.toLowerCase() : '';
    const cat = catFilter ? catFilter.value : 'All';

    let filtered = adminEventsCache.filter(evt => {
      const matchCat = cat === 'All' || evt.category.toLowerCase() === cat.toLowerCase();
      const matchSearch = evt.title.toLowerCase().includes(q) || evt.venue.toLowerCase().includes(q);
      return matchCat && matchSearch;
    });

    renderAdminEventsTable(filtered);
  }

  if (searchInput) searchInput.addEventListener('input', applyFilter);
  if (catFilter) catFilter.addEventListener('change', applyFilter);
}

function openCreateEventModal() {
  selectedEventForEdit = null;
  const form = document.getElementById('event-crud-form');
  if (form) form.reset();

  document.getElementById('event-modal-title').textContent = 'Create New Campus Event';
  document.getElementById('event-id-hidden').value = '';
  document.getElementById('evt-image-preview').src = 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80';
  document.getElementById('evt-image-input').value = 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80';
  
  openModal('event-crud-modal');
}

function openEditEventModal(eventId) {
  const evt = adminEventsCache.find(e => e.id === eventId);
  if (!evt) return;

  selectedEventForEdit = evt;
  document.getElementById('event-modal-title').textContent = 'Edit Campus Event';
  document.getElementById('event-id-hidden').value = evt.id;

  document.getElementById('evt-title-input').value = evt.title;
  document.getElementById('evt-category-input').value = evt.category;
  document.getElementById('evt-date-input').value = evt.date;
  document.getElementById('evt-time-input').value = evt.time;
  document.getElementById('evt-venue-input').value = evt.venue;
  document.getElementById('evt-capacity-input').value = evt.capacity;
  document.getElementById('evt-price-input').value = evt.price;
  document.getElementById('evt-status-input').value = evt.status;
  document.getElementById('evt-desc-input').value = evt.description;
  document.getElementById('evt-image-input').value = evt.image;
  document.getElementById('evt-image-preview').src = evt.image;
  document.getElementById('evt-organizer-input').value = evt.organizer || '';

  openModal('event-crud-modal');
}

function setupEventFormHandlers() {
  const imageInput = document.getElementById('evt-image-input');
  const imagePreview = document.getElementById('evt-image-preview');

  if (imageInput && imagePreview) {
    imageInput.addEventListener('input', () => {
      imagePreview.src = imageInput.value || 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80';
    });
  }

  const form = document.getElementById('event-crud-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const eventId = document.getElementById('event-id-hidden').value;
      const eventData = {
        title: document.getElementById('evt-title-input').value.trim(),
        category: document.getElementById('evt-category-input').value,
        date: document.getElementById('evt-date-input').value,
        time: document.getElementById('evt-time-input').value.trim(),
        venue: document.getElementById('evt-venue-input').value.trim(),
        capacity: parseInt(document.getElementById('evt-capacity-input').value, 10),
        price: parseFloat(document.getElementById('evt-price-input').value) || 0,
        status: document.getElementById('evt-status-input').value,
        description: document.getElementById('evt-desc-input').value.trim(),
        image: document.getElementById('evt-image-input').value.trim(),
        organizer: document.getElementById('evt-organizer-input').value.trim()
      };

      try {
        if (eventId) {
          // Edit
          await api.updateEvent(eventId, eventData);
          showToast('Event updated successfully!', 'success');
        } else {
          // Create
          await api.createEvent(eventData);
          showToast('New event created successfully!', 'success');
        }

        closeModal('event-crud-modal');
        adminEventsCache = await api.getEvents();
        renderAdminEventsTable(adminEventsCache);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }
}

async function handleDeleteEvent(eventId) {
  if (!confirm('Are you sure you want to delete this event? This will also remove all student registrations for this event.')) {
    return;
  }

  try {
    await api.deleteEvent(eventId);
    showToast('Event deleted successfully.', 'info');
    adminEventsCache = await api.getEvents();
    renderAdminEventsTable(adminEventsCache);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

/* ==========================================================================
   3. Admin Registrations & Attendees (admin-registrations.html)
   ========================================================================== */
async function initAdminRegistrations() {
  auth.requireAdmin();

  try {
    adminRegistrationsCache = await api.getRegistrations();
    adminEventsCache = await api.getEvents();

    populateEventFilterDropdown();
    renderAdminRegistrationsTable(adminRegistrationsCache);
    setupRegistrationsFilter();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function populateEventFilterDropdown() {
  const select = document.getElementById('filter-reg-event-select');
  if (!select) return;

  select.innerHTML = '<option value="All">All Events</option>' + 
    adminEventsCache.map(evt => `<option value="${evt.id}">${escapeHtml(evt.title)}</option>`).join('');
}

function renderAdminRegistrationsTable(registrations) {
  const tbody = document.getElementById('admin-registrations-tbody');
  const countEl = document.getElementById('reg-count-display');
  if (!tbody) return;

  if (countEl) countEl.textContent = `${registrations.length} Registrations`;

  if (registrations.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 3rem; color: var(--slate-500);">
          <i class="fa-solid fa-users-slash" style="font-size: 2rem; margin-bottom: 0.5rem; display: block; color: var(--slate-300);"></i>
          No student registrations found for this selection.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = registrations.map(reg => `
    <tr>
      <td>
        <strong>${escapeHtml(reg.userName)}</strong><br/>
        <span style="font-size: 0.775rem; color: var(--slate-500);">${escapeHtml(reg.userEmail)}</span>
      </td>
      <td>${escapeHtml(reg.department || 'N/A')}<br/><small style="color: var(--slate-500);">${escapeHtml(reg.rollNo || '')}</small></td>
      <td><strong>${escapeHtml(reg.eventTitle)}</strong></td>
      <td><code>${escapeHtml(reg.ticketCode)}</code></td>
      <td>${formatDate(reg.registeredAt)}</td>
      <td>
        <button type="button" class="btn btn-sm ${reg.attended ? 'btn-success' : 'btn-secondary'}" onclick="handleToggleAttendance('${reg.id}')">
          <i class="fa-solid ${reg.attended ? 'fa-circle-check' : 'fa-circle'}"></i>
          ${reg.attended ? 'Attended' : 'Mark Present'}
        </button>
      </td>
      <td style="text-align: right;">
        <button type="button" class="btn btn-danger-outline btn-sm" onclick="handleAdminCancelReg('${reg.id}')" title="Revoke Registration">
          <i class="fa-solid fa-user-xmark"></i>
        </button>
      </td>
    </tr>
  `).join('');
}

function setupRegistrationsFilter() {
  const searchInput = document.getElementById('reg-search-input');
  const eventSelect = document.getElementById('filter-reg-event-select');

  function applyFilter() {
    const q = searchInput ? searchInput.value.toLowerCase() : '';
    const selectedEventId = eventSelect ? eventSelect.value : 'All';

    let filtered = adminRegistrationsCache.filter(r => {
      const matchEvent = selectedEventId === 'All' || r.eventId === selectedEventId;
      const matchSearch = r.userName.toLowerCase().includes(q) ||
        r.userEmail.toLowerCase().includes(q) ||
        r.ticketCode.toLowerCase().includes(q) ||
        r.eventTitle.toLowerCase().includes(q);
      return matchEvent && matchSearch;
    });

    renderAdminRegistrationsTable(filtered);
  }

  if (searchInput) searchInput.addEventListener('input', applyFilter);
  if (eventSelect) eventSelect.addEventListener('change', applyFilter);
}

async function handleToggleAttendance(regId) {
  try {
    const updated = await api.toggleAttendance(regId);
    showToast(`Attendance updated for ${updated.userName}`, 'info');
    adminRegistrationsCache = await api.getRegistrations();
    setupRegistrationsFilter();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function handleAdminCancelReg(regId) {
  if (!confirm('Are you sure you want to cancel this student registration?')) return;

  try {
    await api.cancelRegistration(regId);
    showToast('Registration cancelled and seat freed.', 'info');
    adminRegistrationsCache = await api.getRegistrations();
    setupRegistrationsFilter();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

/* ==========================================================================
   4. Client-side CSV Export Utility
   ========================================================================== */
function exportRegistrationsToCSV() {
  if (!adminRegistrationsCache || adminRegistrationsCache.length === 0) {
    showToast('No registrations to export', 'warning');
    return;
  }

  const headers = ['Registration ID', 'Student Name', 'Email', 'Department', 'Roll No', 'Event Title', 'Ticket Code', 'Registration Date', 'Attended'];
  const rows = adminRegistrationsCache.map(r => [
    `"${r.id}"`,
    `"${r.userName}"`,
    `"${r.userEmail}"`,
    `"${r.department || ''}"`,
    `"${r.rollNo || ''}"`,
    `"${r.eventTitle.replace(/"/g, '""')}"`,
    `"${r.ticketCode}"`,
    `"${r.registeredAt}"`,
    `"${r.attended ? 'Yes' : 'No'}"`
  ]);

  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `campushub_registrations_${new Date().toISOString().slice(0,10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast('Registrations exported to CSV!', 'success');
}
