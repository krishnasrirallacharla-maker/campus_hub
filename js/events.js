/**
 * CampusHub - Events Discovery, Filter & Details Controller
 */

let allEventsCache = [];
let currentFilterCategory = 'All';
let currentSort = 'date-asc';
let currentSearchQuery = '';

/* ==========================================================================
   1. Events Catalog Page (events.html) & Home Highlights (index.html)
   ========================================================================== */
async function loadEventsCatalog(options = {}) {
  const container = document.getElementById('events-grid-container');
  if (!container) return;

  try {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 3rem;">
        <i class="fa-solid fa-spinner fa-spin" style="font-size: 2rem; color: var(--primary-600);"></i>
        <p style="margin-top: 0.75rem; color: var(--slate-500);">Loading events...</p>
      </div>
    `;

    allEventsCache = await api.getEvents();
    
    // If on homepage and limit requested
    if (options.limit) {
      renderEventsList(allEventsCache.slice(0, options.limit), container);
      return;
    }

    renderFilteredEvents();
    setupCatalogControls();
  } catch (err) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon"><i class="fa-solid fa-triangle-exclamation"></i></div>
        <h3>Failed to load events</h3>
        <p>${escapeHtml(err.message)}</p>
      </div>
    `;
  }
}

function renderFilteredEvents() {
  const container = document.getElementById('events-grid-container');
  const countBadge = document.getElementById('events-count-badge');
  if (!container) return;

  let filtered = [...allEventsCache];

  // Category filter
  if (currentFilterCategory && currentFilterCategory !== 'All') {
    filtered = filtered.filter(e => e.category.toLowerCase() === currentFilterCategory.toLowerCase());
  }

  // Search filter
  if (currentSearchQuery.trim()) {
    const q = currentSearchQuery.toLowerCase();
    filtered = filtered.filter(e => 
      e.title.toLowerCase().includes(q) ||
      e.description.toLowerCase().includes(q) ||
      e.venue.toLowerCase().includes(q) ||
      e.category.toLowerCase().includes(q)
    );
  }

  // Sorting
  if (currentSort === 'date-asc') {
    filtered.sort((a, b) => new Date(a.date) - new Date(b.date));
  } else if (currentSort === 'date-desc') {
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
  } else if (currentSort === 'popular') {
    filtered.sort((a, b) => b.registeredCount - a.registeredCount);
  } else if (currentSort === 'price-low') {
    filtered.sort((a, b) => a.price - b.price);
  }

  if (countBadge) {
    countBadge.textContent = `${filtered.length} Event${filtered.length === 1 ? '' : 's'}`;
  }

  renderEventsList(filtered, container);
}

function renderEventsList(events, container) {
  if (events.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon"><i class="fa-solid fa-calendar-xmark"></i></div>
        <h3>No Events Found</h3>
        <p>Try clearing your search filters or check back later for newly scheduled campus events.</p>
        <button type="button" class="btn btn-secondary btn-sm" onclick="resetFilters()">Reset Filters</button>
      </div>
    `;
    return;
  }

  const currentUser = auth.getCurrentUser();
  const registrations = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');
  const registeredEventIds = new Set(
    currentUser ? registrations.filter(r => r.userId === currentUser.id).map(r => r.eventId) : []
  );

  container.innerHTML = events.map(event => {
    const isRegistered = registeredEventIds.has(event.id);
    const fillPercent = Math.min(100, Math.round((event.registeredCount / event.capacity) * 100));
    const isFull = event.registeredCount >= event.capacity;
    const catClass = `badge-${event.category.toLowerCase()}`;

    return `
      <article class="event-card">
        <div class="event-card-media">
          <img src="${escapeHtml(event.image)}" alt="${escapeHtml(event.title)}" loading="lazy" />
          <span class="badge ${catClass} event-card-cat-badge">${escapeHtml(event.category)}</span>
          <div class="event-card-date-badge">
            <i class="fa-regular fa-calendar"></i>
            <span>${formatDate(event.date)}</span>
          </div>
        </div>

        <div class="event-card-body">
          <h3 class="event-card-title">
            <a href="event-details.html?id=${encodeURIComponent(event.id)}">${escapeHtml(event.title)}</a>
          </h3>
          <p class="event-card-desc">${escapeHtml(event.description)}</p>

          <div class="event-meta-list">
            <div class="event-meta-item">
              <i class="fa-regular fa-clock"></i>
              <span>${escapeHtml(event.time)}</span>
            </div>
            <div class="event-meta-item">
              <i class="fa-solid fa-location-dot"></i>
              <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${escapeHtml(event.venue)}</span>
            </div>
          </div>

          <div class="capacity-container">
            <div class="capacity-header">
              <span>Seats: ${event.registeredCount} / ${event.capacity}</span>
              <span>${isFull ? 'Sold Out' : `${event.capacity - event.registeredCount} spots left`}</span>
            </div>
            <div class="capacity-bar-bg">
              <div class="capacity-bar-fill ${fillPercent > 85 ? 'warning' : ''} ${isFull ? 'full' : ''}" style="width: ${fillPercent}%"></div>
            </div>
          </div>

          <div class="event-card-footer">
            <div class="event-card-price ${event.price === 0 ? 'free' : ''}">
              ${formatPrice(event.price)}
            </div>

            <div style="display: flex; gap: 0.5rem;">
              <a href="event-details.html?id=${encodeURIComponent(event.id)}" class="btn btn-outline btn-sm">
                Details
              </a>
              ${isRegistered ? `
                <span class="btn btn-success btn-sm" style="cursor: default;">
                  <i class="fa-solid fa-check"></i> Registered
                </span>
              ` : `
                <button type="button" class="btn btn-primary btn-sm" ${isFull ? 'disabled' : ''} onclick="handleQuickRegister('${event.id}')">
                  ${isFull ? 'Full' : 'Register'}
                </button>
              `}
            </div>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

function setupCatalogControls() {
  // Category Pill Clicks
  const catButtons = document.querySelectorAll('.cat-pill-btn');
  catButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      catButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilterCategory = btn.dataset.category || 'All';
      renderFilteredEvents();
    });
  });

  // Search Input
  const searchInput = document.getElementById('catalog-search-input');
  if (searchInput) {
    let timeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        currentSearchQuery = e.target.value;
        renderFilteredEvents();
      }, 250);
    });
  }

  // Sort Dropdown
  const sortSelect = document.getElementById('catalog-sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      currentSort = e.target.value;
      renderFilteredEvents();
    });
  }
}

function resetFilters() {
  currentFilterCategory = 'All';
  currentSearchQuery = '';
  currentSort = 'date-asc';

  const searchInput = document.getElementById('catalog-search-input');
  if (searchInput) searchInput.value = '';

  const sortSelect = document.getElementById('catalog-sort-select');
  if (sortSelect) sortSelect.value = 'date-asc';

  document.querySelectorAll('.cat-pill-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.category === 'All');
  });

  renderFilteredEvents();
}

/* ==========================================================================
   2. Single Event Details Page (event-details.html)
   ========================================================================== */
let currentEventDetail = null;

async function loadEventDetails() {
  const params = new URLSearchParams(window.location.search);
  const eventId = params.get('id');

  if (!eventId) {
    window.location.href = 'events.html';
    return;
  }

  try {
    currentEventDetail = await api.getEvent(eventId);
    renderEventDetailView(currentEventDetail);
    startCountdown(currentEventDetail.date);
    checkUserRegistrationStatus(currentEventDetail.id);
  } catch (err) {
    document.getElementById('event-detail-container').innerHTML = `
      <div class="container section">
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fa-solid fa-triangle-exclamation"></i></div>
          <h2>Event Not Found</h2>
          <p>The event you are looking for may have been removed or does not exist.</p>
          <a href="events.html" class="btn btn-primary">Browse All Events</a>
        </div>
      </div>
    `;
  }
}

function renderEventDetailView(evt) {
  document.title = `${evt.title} - CampusHub`;

  // Breadcrumbs & titles
  document.getElementById('detail-breadcrumb-title').textContent = evt.title;
  document.getElementById('detail-event-title').textContent = evt.title;
  document.getElementById('detail-event-badge').className = `badge badge-${evt.category.toLowerCase()}`;
  document.getElementById('detail-event-badge').textContent = evt.category;
  document.getElementById('detail-event-date').textContent = formatDate(evt.date);
  document.getElementById('detail-event-time').textContent = evt.time;
  document.getElementById('detail-event-venue').textContent = evt.venue;
  document.getElementById('detail-event-organizer').textContent = evt.organizer || 'Campus Event Committee';

  // Hero image
  document.getElementById('detail-hero-img').src = evt.image;
  document.getElementById('detail-hero-img').alt = evt.title;

  // Description
  document.getElementById('detail-full-description').textContent = evt.fullDescription || evt.description;

  // Ticket Box
  document.getElementById('detail-ticket-price').textContent = formatPrice(evt.price);
  document.getElementById('detail-seats-left').textContent = `${evt.capacity - evt.registeredCount} spots`;
  document.getElementById('detail-total-capacity').textContent = `${evt.capacity} students`;

  // Schedule Timeline
  const timelineBox = document.getElementById('detail-timeline-container');
  if (timelineBox && evt.schedule && evt.schedule.length > 0) {
    timelineBox.innerHTML = evt.schedule.map(item => `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-time">${escapeHtml(item.time)}</div>
        <div class="timeline-title">${escapeHtml(item.title)}</div>
        <div class="timeline-desc">${escapeHtml(item.desc || '')}</div>
      </div>
    `).join('');
  }

  // Speakers Grid
  const speakersBox = document.getElementById('detail-speakers-container');
  if (speakersBox && evt.speakers && evt.speakers.length > 0) {
    speakersBox.innerHTML = evt.speakers.map(spk => `
      <div class="speaker-card">
        <img src="${escapeHtml(spk.avatar)}" alt="${escapeHtml(spk.name)}" class="speaker-avatar" />
        <div class="speaker-name">${escapeHtml(spk.name)}</div>
        <div class="speaker-title">${escapeHtml(spk.title)}</div>
      </div>
    `).join('');
  }
}

function startCountdown(dateStr) {
  const targetDate = new Date(dateStr).getTime();
  const daysEl = document.getElementById('cd-days');
  const hoursEl = document.getElementById('cd-hours');
  const minsEl = document.getElementById('cd-mins');
  const secsEl = document.getElementById('cd-secs');

  if (!daysEl) return;

  function update() {
    const now = new Date().getTime();
    const diff = targetDate - now;

    if (diff <= 0) {
      daysEl.textContent = '00';
      hoursEl.textContent = '00';
      minsEl.textContent = '00';
      secsEl.textContent = '00';
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const secs = Math.floor((diff % (1000 * 60)) / 1000);

    daysEl.textContent = String(days).padStart(2, '0');
    hoursEl.textContent = String(hours).padStart(2, '0');
    minsEl.textContent = String(mins).padStart(2, '0');
    secsEl.textContent = String(secs).padStart(2, '0');
  }

  update();
  setInterval(update, 1000);
}

function checkUserRegistrationStatus(eventId) {
  const btnContainer = document.getElementById('detail-register-btn-container');
  if (!btnContainer) return;

  const currentUser = auth.getCurrentUser();
  if (!currentUser) {
    btnContainer.innerHTML = `
      <a href="login.html?redirect=${encodeURIComponent(window.location.href)}" class="btn btn-primary btn-block btn-lg">
        Log In to Register
      </a>
    `;
    return;
  }

  const registrations = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');
  const existingReg = registrations.find(r => r.eventId === eventId && r.userId === currentUser.id);

  if (existingReg) {
    btnContainer.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 0.75rem;">
        <div class="badge badge-success" style="padding: 0.6rem; justify-content: center; font-size: 0.95rem;">
          <i class="fa-solid fa-circle-check"></i> You are registered!
        </div>
        <button type="button" class="btn btn-secondary btn-block" onclick="showTicketPassModal('${existingReg.id}')">
          <i class="fa-solid fa-qrcode"></i> View Pass & Ticket
        </button>
        <button type="button" class="btn btn-danger-outline btn-block btn-sm" onclick="handleCancelDetailRegistration('${existingReg.id}')">
          Cancel Registration
        </button>
      </div>
    `;
  } else {
    const isFull = currentEventDetail && currentEventDetail.registeredCount >= currentEventDetail.capacity;
    btnContainer.innerHTML = `
      <button type="button" class="btn btn-primary btn-block btn-lg" ${isFull ? 'disabled' : ''} onclick="handleRegisterSubmit()">
        ${isFull ? 'Event Full (Waitlist)' : 'Confirm Registration'}
      </button>
    `;
  }
}

/* ==========================================================================
   3. Quick Register & Detail Register Actions
   ========================================================================== */
async function handleQuickRegister(eventId) {
  const currentUser = auth.getCurrentUser();
  if (!currentUser) {
    window.location.href = `login.html?redirect=${encodeURIComponent(window.location.href)}`;
    return;
  }

  try {
    const reg = await api.registerForEvent(eventId, currentUser);
    showToast(`Successfully registered for ${reg.eventTitle}!`, 'success');
    allEventsCache = await api.getEvents();
    renderFilteredEvents();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function handleRegisterSubmit() {
  const currentUser = auth.getCurrentUser();
  if (!currentUser || !currentEventDetail) return;

  try {
    const reg = await api.registerForEvent(currentEventDetail.id, currentUser);
    showToast(`You have registered successfully! Ticket #${reg.ticketCode}`, 'success');
    currentEventDetail.registeredCount += 1;
    renderEventDetailView(currentEventDetail);
    checkUserRegistrationStatus(currentEventDetail.id);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function handleCancelDetailRegistration(regId) {
  if (!confirm('Are you sure you want to cancel your registration? Your spot will be released.')) return;

  try {
    await api.cancelRegistration(regId);
    showToast('Registration cancelled successfully.', 'info');
    currentEventDetail = await api.getEvent(currentEventDetail.id);
    renderEventDetailView(currentEventDetail);
    checkUserRegistrationStatus(currentEventDetail.id);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function showTicketPassModal(regId) {
  const registrations = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');
  const reg = registrations.find(r => r.id === regId);
  if (!reg) return;

  document.getElementById('pass-event-title').textContent = reg.eventTitle;
  document.getElementById('pass-student-name').textContent = reg.userName;
  document.getElementById('pass-ticket-code').textContent = reg.ticketCode;
  document.getElementById('pass-date-time').textContent = `${formatDate(reg.eventDate)}`;
  document.getElementById('pass-venue').textContent = reg.eventVenue;
  document.getElementById('pass-status-badge').textContent = reg.status;

  openModal('ticket-pass-modal');
}
