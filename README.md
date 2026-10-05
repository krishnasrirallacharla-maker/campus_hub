# 🎓 CampusHub - College Event Management System (Frontend)

A modern, responsive, and feature-rich **College Event Management System Frontend** built using **pure HTML5, CSS3 (Custom Properties & Design Tokens), and Vanilla JavaScript (ES6+)**.

---

## 🌟 Key Features

### 1. 🏠 Public & Student Discovery
- **Hero & Highlights**: Dynamic landing page showcasing upcoming campus events, statistics counters, and categorized filters.
- **Events Catalog (`events.html`)**: Real-time keyword search, category pills (Tech, Cultural, Workshop, Sports, Gaming, Seminar), sorting by date, popularity, or price.
- **Single Event Details (`event-details.html`)**:
  - Live countdown timer.
  - Event agenda schedule timeline.
  - Speaker cards with bios.
  - Sticky registration & capacity status indicator.
  - Instant seat reservation with dynamic capacity counter.

### 2. 🎟️ Student Portal & Passes
- **Student Dashboard (`student-dashboard.html`)**: Personalized overview with key metrics (Registered events, Upcoming this week, Completed events).
- **My Passes (`my-events.html`)**: View digital ticket passes, filter active vs past passes, cancel registration, and view interactive digital QR code passes.
- **Profile Settings (`profile.html`)**: View and update academic department, roll number, semester, bio, and contact information.

### 3. 🛡️ Admin & Organizer Center
- **Admin Dashboard (`admin-dashboard.html`)**: Real-time aggregate statistics (Total Events, Registrations, Student engagement, and Capacity Fill Rate percentage).
- **Event CRUD Manager (`admin-events.html`)**:
  - Create new events with banner image preview.
  - Edit existing event details, time slots, seat capacities, and publishing status.
  - Delete events with instant cascade registration cleanup.
- **Registrations & Attendee List (`admin-registrations.html`)**:
  - Filter registrations by specific event.
  - Search attendees by student name, email, or ticket code.
  - 1-click **Attendance Check-in Toggle** (Attended / Present).
  - Client-side **Export to CSV** for offline attendance sheets and reporting.

---

## 🚀 Quick Start / Demo Credentials

No build step or npm packages required! Simply open `index.html` in any modern web browser or run a local static server:

```bash
# Optional: Using Python built-in HTTP server
python -m http.server 8000
```

### Pre-loaded Demo Accounts:
| Role | Email | Password |
| :--- | :--- | :--- |
| **Student** | `student@college.edu` | `password123` |
| **Admin / Faculty** | `admin@college.edu` | `admin123` |

*(You can also use the 1-click Demo Fill buttons on the [Login Page](login.html) or register new accounts freely.)*

---

## 📁 Project Structure

```
frontend/
├── index.html                   # Landing page
├── events.html                  # Events discovery & filter catalog
├── event-details.html           # Single event view with countdown & registration
├── login.html                   # Login page with demo account shortcuts
├── register.html                # Account registration with student/admin roles
├── student-dashboard.html       # Student dashboard overview
├── my-events.html               # Student registered passes & QR tickets
├── profile.html                 # Profile editor
├── admin-dashboard.html         # Admin command center & analytics
├── admin-events.html            # Admin event CRUD operations
├── admin-registrations.html     # Admin attendee manager & CSV export
├── css/
│   ├── variables.css            # Purple / Blue color palette & design tokens
│   ├── main.css                 # Base layout, navbar, footer, modals & toasts
│   ├── events.css               # Event cards, discovery filters & countdowns
│   ├── dashboard.css            # Sidebar layouts, stat cards & data tables
│   └── auth.css                 # Authentication cards & role selector
├── js/
│   ├── mock-data.js             # Initial database & localStorage seeder
│   ├── api.js                   # REST-ready async service layer
│   ├── auth.js                  # Authentication & route guards
│   ├── main.js                  # Global navbar sync, toasts & modal helpers
│   ├── events.js                # Events discovery & single detail handlers
│   ├── student-dashboard.js     # Student stats & ticket pass rendering
│   ├── admin.js                 # Admin CRUD & registrations logic
│   └── profile.js               # Profile update controller
└── assets/
    └── images/                  # Static assets
```

---

## 🔌 Connecting to a Python Flask REST API Backend

The JavaScript architecture in `js/api.js` is built with `async/await` and follows standard REST endpoint patterns. When you build your Flask backend, swap the `localStorage` operations with `fetch()` calls as shown below:

```javascript
// Example in js/api.js:
const API_BASE_URL = 'http://localhost:5000/api';

async getEvents(filters = {}) {
  const response = await fetch(`${API_BASE_URL}/events`);
  return await response.json();
}

async createEvent(eventData) {
  const response = await fetch(`${API_BASE_URL}/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(eventData)
  });
  return await response.json();
}
```

### Corresponding Flask Routes Reference:
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/register` - Create user account
- `GET /api/events` - Get list of events
- `POST /api/events` - Create event (Admin)
- `GET /api/events/<id>` - Single event details
- `PUT /api/events/<id>` - Update event (Admin)
- `DELETE /api/events/<id>` - Delete event (Admin)
- `GET /api/registrations` - List registrations
- `POST /api/registrations` - Register for an event
- `DELETE /api/registrations/<id>` - Cancel registration
- `GET /api/dashboard/stats` - Aggregate metrics
