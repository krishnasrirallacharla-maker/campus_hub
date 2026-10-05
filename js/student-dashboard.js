/**
 * CampusHub - Student Dashboard & My Events Controller
 */

/* ==========================================================================
   1. Student Dashboard Overview (student-dashboard.html)
   ========================================================================== */
async function initStudentDashboard() {
  auth.requireAuth();

  const user = auth.getCurrentUser();
  if (user.role === 'admin') {
    window.location.href = 'admin-dashboard.html';
    return;
  }

  // Update user header info
  const nameEl = document.getElementById('student-greeting-name');
  if (nameEl) nameEl.textContent = user.name;

  const deptEl = document.getElementById('student-dept-tag');
  if (deptEl) deptEl.textContent = `${user.department} • ${user.rollNo || 'Student'}`;

  loadStudentStatsAndEvents(user.id);
}

async function loadStudentStatsAndEvents(userId) {
  try {
    const userRegs = await api.getRegistrations({ userId });
    const allEvents = await api.getEvents();

    const now = new Date();
    const upcoming = userRegs.filter(r => new Date(r.eventDate) >= now || isToday(new Date(r.eventDate)));
    const past = userRegs.filter(r => new Date(r.eventDate) < now && !isToday(new Date(r.eventDate)));

    // Update Stats
    const totalRegsEl = document.getElementById('stat-total-registered');
    if (totalRegsEl) totalRegsEl.textContent = userRegs.length;

    const upcomingEl = document.getElementById('stat-upcoming-count');
    if (upcomingEl) upcomingEl.textContent = upcoming.length;

    const pastEl = document.getElementById('stat-attended-count');
    if (pastEl) pastEl.textContent = past.length;

    // Render Recent Registered Events Table / List
    const tableBody = document.getElementById('student-recent-events-tbody');
    if (tableBody) {
      if (userRegs.length === 0) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align: center; padding: 2.5rem 1rem; color: var(--slate-500);">
              <i class="fa-solid fa-ticket-simple" style="font-size: 2rem; margin-bottom: 0.75rem; color: var(--primary-300); display: block;"></i>
              You haven't registered for any campus events yet.
              <div style="margin-top: 1rem;">
                <a href="events.html" class="btn btn-primary btn-sm">Explore Events</a>
              </div>
            </td>
          </tr>
        `;
      } else {
        tableBody.innerHTML = userRegs.slice(0, 5).map(reg => {
          const matchedEvt = allEvents.find(e => e.id === reg.eventId) || {};
          const isUpcoming = new Date(reg.eventDate) >= new Date();

          return `
            <tr>
              <td>
                <div class="table-event-cell">
                  <img src="${matchedEvt.image || 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=150&q=80'}" class="table-event-thumb" alt="" />
                  <div class="table-event-info">
                    <span class="table-event-title">${escapeHtml(reg.eventTitle)}</span>
                    <span class="table-event-date"><i class="fa-regular fa-calendar"></i> ${formatDate(reg.eventDate)}</span>
                  </div>
                </div>
              </td>
              <td><code>${escapeHtml(reg.ticketCode)}</code></td>
              <td>${escapeHtml(reg.eventVenue)}</td>
              <td>
                <span class="badge ${isUpcoming ? 'badge-tech' : 'badge-secondary'}">
                  ${isUpcoming ? 'Upcoming' : 'Completed'}
                </span>
              </td>
              <td style="text-align: right;">
                <button type="button" class="btn btn-secondary btn-sm" onclick="showTicketModal('${reg.id}')">
                  <i class="fa-solid fa-qrcode"></i> View Pass
                </button>
              </td>
            </tr>
          `;
        }).join('');
      }
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

/* ==========================================================================
   2. My Registered Events Catalog (my-events.html)
   ========================================================================== */
let myEventsCache = [];
let activeMyEventsTab = 'all';

async function initMyEventsPage() {
  auth.requireAuth();
  const user = auth.getCurrentUser();

  try {
    myEventsCache = await api.getRegistrations({ userId: user.id });
    renderMyEventsGrid();
    setupMyEventsTabs();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderMyEventsGrid() {
  const container = document.getElementById('my-events-grid');
  if (!container) return;

  const now = new Date();
  let filtered = [...myEventsCache];

  if (activeMyEventsTab === 'upcoming') {
    filtered = filtered.filter(r => new Date(r.eventDate) >= now || isToday(new Date(r.eventDate)));
  } else if (activeMyEventsTab === 'past') {
    filtered = filtered.filter(r => new Date(r.eventDate) < now && !isToday(new Date(r.eventDate)));
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon"><i class="fa-solid fa-ticket-simple"></i></div>
        <h3>No ${activeMyEventsTab === 'all' ? '' : activeMyEventsTab} Registrations</h3>
        <p>Discover new hackathons, cultural festivals, sports matches and workshops on CampusHub.</p>
        <a href="events.html" class="btn btn-primary">Browse Events</a>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(reg => {
    const isUpcoming = new Date(reg.eventDate) >= now || isToday(new Date(reg.eventDate));

    return `
      <div class="ticket-card">
        <div class="ticket-card-header">
          <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; opacity: 0.9;">Official Event Pass</div>
            <div style="font-size: 0.9rem; font-weight: 700;">${escapeHtml(reg.ticketCode)}</div>
          </div>
          <span class="ticket-badge">${isUpcoming ? 'Active Pass' : 'Completed'}</span>
        </div>

        <div class="ticket-card-body">
          <div class="ticket-event-name">${escapeHtml(reg.eventTitle)}</div>
          
          <div class="ticket-meta-grid">
            <div>
              <div class="ticket-meta-label">Date</div>
              <div class="ticket-meta-val">${formatDate(reg.eventDate)}</div>
            </div>
            <div>
              <div class="ticket-meta-label">Status</div>
              <div class="ticket-meta-val" style="color: var(--success-600);"><i class="fa-solid fa-circle-check"></i> Confirmed</div>
            </div>
            <div style="grid-column: 1/-1;">
              <div class="ticket-meta-label">Venue</div>
              <div class="ticket-meta-val">${escapeHtml(reg.eventVenue)}</div>
            </div>
          </div>
        </div>

        <div class="ticket-card-footer">
          <button type="button" class="btn btn-primary btn-sm" onclick="showTicketModal('${reg.id}')">
            <i class="fa-solid fa-qrcode"></i> Show Digital Pass
          </button>
          ${isUpcoming ? `
            <button type="button" class="btn btn-danger-outline btn-sm" onclick="handleStudentCancelRegistration('${reg.id}')">
              Cancel
            </button>
          ` : `
            <span class="badge badge-secondary">Event Concluded</span>
          `}
        </div>
      </div>
    `;
  }).join('');
}

function setupMyEventsTabs() {
  document.querySelectorAll('.my-events-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.my-events-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeMyEventsTab = btn.dataset.tab;
      renderMyEventsGrid();
    });
  });
}

async function handleStudentCancelRegistration(regId) {
  if (!confirm('Are you sure you want to cancel this event registration? Your ticket will be invalidated.')) {
    return;
  }

  try {
    await api.cancelRegistration(regId);
    showToast('Registration cancelled.', 'info');
    const user = auth.getCurrentUser();
    myEventsCache = await api.getRegistrations({ userId: user.id });
    renderMyEventsGrid();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function showTicketModal(regId) {
  const reg = myEventsCache.find(r => r.id === regId) || JSON.parse(localStorage.getItem('campushub_registrations') || '[]').find(r => r.id === regId);
  if (!reg) return;

  document.getElementById('pass-event-title').textContent = reg.eventTitle;
  document.getElementById('pass-student-name').textContent = reg.userName;
  document.getElementById('pass-ticket-code').textContent = reg.ticketCode;
  document.getElementById('pass-date-time').textContent = formatDate(reg.eventDate);
  document.getElementById('pass-venue').textContent = reg.eventVenue;
  document.getElementById('pass-status-badge').textContent = reg.status || 'Confirmed';

  openModal('ticket-pass-modal');
}

function isToday(date) {
  const today = new Date();
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear();
}
