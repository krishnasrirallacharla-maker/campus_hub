/**
 * CampusHub API Service Layer
 * 
 * NOTE FOR BACKEND INTEGRATION:
 * This module is designed with async/await methods and REST conventions.
 * To connect to your Python Flask REST API backend, replace the localStorage operations
 * with standard `fetch('http://localhost:5000/api/...')` calls!
 */

const API_BASE_URL = 'http://localhost:5000/api'; // Future Flask backend URL

const api = {
  // ==========================================
  // 1. AUTHENTICATION & USERS
  // ==========================================

  /**
   * Login user with email & password
   * Flask endpoint: POST /api/auth/login
   */
  async login(email, password) {
    // Simulated network delay
    await this._delay(150);

    const users = JSON.parse(localStorage.getItem('campushub_users') || '[]');
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase() && u.password === password);

    if (!user) {
      throw new Error('Invalid email or password. Please try again.');
    }

    const { password: _, ...safeUser } = user;
    return { success: true, user: safeUser, token: 'mock-jwt-token-' + Date.now() };
  },

  /**
   * Register a new student or organizer
   * Flask endpoint: POST /api/auth/register
   */
  async register(userData) {
    await this._delay(200);

    const users = JSON.parse(localStorage.getItem('campushub_users') || '[]');
    const existing = users.find(u => u.email.toLowerCase() === userData.email.toLowerCase());

    if (existing) {
      throw new Error('An account with this email already exists.');
    }

    const newUser = {
      id: 'usr_' + Date.now(),
      name: userData.name,
      email: userData.email,
      password: userData.password,
      role: userData.role || 'student',
      department: userData.department || 'General',
      rollNo: userData.rollNo || 'N/A',
      semester: userData.semester || 'N/A',
      phone: userData.phone || '',
      bio: userData.bio || 'New member of CampusHub.',
      avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80'
    };

    users.push(newUser);
    localStorage.setItem('campushub_users', JSON.stringify(users));

    const { password: _, ...safeUser } = newUser;
    return { success: true, user: safeUser };
  },

  /**
   * Get user profile by ID
   * Flask endpoint: GET /api/users/<id>
   */
  async getUserProfile(userId) {
    const users = JSON.parse(localStorage.getItem('campushub_users') || '[]');
    const user = users.find(u => u.id === userId);
    if (!user) throw new Error('User not found');
    const { password: _, ...safeUser } = user;
    return safeUser;
  },

  /**
   * Update user profile
   * Flask endpoint: PUT /api/users/<id>
   */
  async updateUserProfile(userId, updateData) {
    await this._delay(150);
    let users = JSON.parse(localStorage.getItem('campushub_users') || '[]');
    const index = users.findIndex(u => u.id === userId);
    if (index === -1) throw new Error('User not found');

    users[index] = { ...users[index], ...updateData };
    localStorage.setItem('campushub_users', JSON.stringify(users));

    const { password: _, ...safeUser } = users[index];
    return safeUser;
  },

  // ==========================================
  // 2. EVENTS MANAGEMENT (CRUD)
  // ==========================================

  /**
   * Get list of all events with optional filtering
   * Flask endpoint: GET /api/events
   */
  async getEvents(filters = {}) {
    await this._delay(100);
    let events = JSON.parse(localStorage.getItem('campushub_events') || '[]');

    if (filters.category && filters.category !== 'All') {
      events = events.filter(e => e.category.toLowerCase() === filters.category.toLowerCase());
    }
    if (filters.search) {
      const q = filters.search.toLowerCase();
      events = events.filter(e => 
        e.title.toLowerCase().includes(q) || 
        e.description.toLowerCase().includes(q) ||
        e.venue.toLowerCase().includes(q)
      );
    }
    if (filters.status) {
      events = events.filter(e => e.status.toLowerCase() === filters.status.toLowerCase());
    }

    // Sort by date (upcoming first)
    return events.sort((a, b) => new Date(a.date) - new Date(b.date));
  },

  /**
   * Get single event by ID
   * Flask endpoint: GET /api/events/<id>
   */
  async getEvent(id) {
    await this._delay(100);
    const events = JSON.parse(localStorage.getItem('campushub_events') || '[]');
    const event = events.find(e => e.id === id);
    if (!event) throw new Error('Event not found');
    return event;
  },

  /**
   * Create new event (Admin)
   * Flask endpoint: POST /api/events
   */
  async createEvent(eventData) {
    await this._delay(200);
    const events = JSON.parse(localStorage.getItem('campushub_events') || '[]');

    const newEvent = {
      id: 'evt_' + Date.now(),
      title: eventData.title,
      category: eventData.category || 'Tech',
      description: eventData.description,
      fullDescription: eventData.fullDescription || eventData.description,
      date: eventData.date,
      time: eventData.time || '10:00 AM - 04:00 PM',
      venue: eventData.venue,
      capacity: parseInt(eventData.capacity, 10) || 100,
      registeredCount: 0,
      price: parseFloat(eventData.price) || 0,
      status: eventData.status || 'Published',
      image: eventData.image || 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80',
      organizer: eventData.organizer || 'Campus Event Committee',
      schedule: eventData.schedule || [
        { time: '10:00 AM', title: 'Welcome & Introduction', desc: 'Opening speech and registration' },
        { time: '11:30 AM', title: 'Main Sessions', desc: 'Core presentations and activities' },
        { time: '03:30 PM', title: 'Closing & Wrap-up', desc: 'Awards and certificates distribution' }
      ],
      speakers: eventData.speakers || [
        { name: 'Dr. Guest Speaker', title: 'Keynote Speaker', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80' }
      ]
    };

    events.unshift(newEvent);
    localStorage.setItem('campushub_events', JSON.stringify(events));
    return newEvent;
  },

  /**
   * Update existing event (Admin)
   * Flask endpoint: PUT /api/events/<id>
   */
  async updateEvent(id, eventData) {
    await this._delay(200);
    let events = JSON.parse(localStorage.getItem('campushub_events') || '[]');
    const index = events.findIndex(e => e.id === id);
    if (index === -1) throw new Error('Event not found');

    events[index] = {
      ...events[index],
      ...eventData,
      capacity: parseInt(eventData.capacity || events[index].capacity, 10),
      price: parseFloat(eventData.price !== undefined ? eventData.price : events[index].price)
    };

    localStorage.setItem('campushub_events', JSON.stringify(events));
    return events[index];
  },

  /**
   * Delete an event (Admin)
   * Flask endpoint: DELETE /api/events/<id>
   */
  async deleteEvent(id) {
    await this._delay(150);
    let events = JSON.parse(localStorage.getItem('campushub_events') || '[]');
    events = events.filter(e => e.id !== id);
    localStorage.setItem('campushub_events', JSON.stringify(events));

    // Also remove registrations related to this event
    let regs = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');
    regs = regs.filter(r => r.eventId !== id);
    localStorage.setItem('campushub_registrations', JSON.stringify(regs));

    return { success: true, message: 'Event deleted successfully.' };
  },

  // ==========================================
  // 3. REGISTRATIONS & TICKETS
  // ==========================================

  /**
   * Register a user for an event
   * Flask endpoint: POST /api/registrations
   */
  async registerForEvent(eventId, user) {
    await this._delay(200);
    let events = JSON.parse(localStorage.getItem('campushub_events') || '[]');
    let registrations = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');

    const eventIndex = events.findIndex(e => e.id === eventId);
    if (eventIndex === -1) throw new Error('Event not found');

    const event = events[eventIndex];

    // Check if already registered
    const alreadyRegistered = registrations.some(r => r.eventId === eventId && r.userId === user.id);
    if (alreadyRegistered) {
      throw new Error('You are already registered for this event!');
    }

    // Check capacity
    if (event.registeredCount >= event.capacity) {
      throw new Error('Sorry! This event has reached maximum capacity.');
    }

    // Create registration
    const newRegistration = {
      id: 'reg_' + Date.now(),
      eventId: event.id,
      userId: user.id,
      userName: user.name,
      userEmail: user.email,
      department: user.department || 'N/A',
      rollNo: user.rollNo || 'N/A',
      eventTitle: event.title,
      eventDate: event.date,
      eventVenue: event.venue,
      ticketCode: 'CH-' + Math.random().toString(36).substring(2, 6).toUpperCase() + '-' + Math.floor(1000 + Math.random() * 9000),
      registeredAt: new Date().toISOString(),
      status: 'Confirmed',
      attended: false
    };

    registrations.unshift(newRegistration);
    localStorage.setItem('campushub_registrations', JSON.stringify(registrations));

    // Increment event registeredCount
    events[eventIndex].registeredCount += 1;
    localStorage.setItem('campushub_events', JSON.stringify(events));

    return newRegistration;
  },

  /**
   * Cancel an event registration
   * Flask endpoint: DELETE /api/registrations/<id>
   */
  async cancelRegistration(registrationId) {
    await this._delay(150);
    let registrations = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');
    let events = JSON.parse(localStorage.getItem('campushub_events') || '[]');

    const reg = registrations.find(r => r.id === registrationId);
    if (!reg) throw new Error('Registration not found');

    // Remove registration
    registrations = registrations.filter(r => r.id !== registrationId);
    localStorage.setItem('campushub_registrations', JSON.stringify(registrations));

    // Decrement event counter
    const eventIndex = events.findIndex(e => e.id === reg.eventId);
    if (eventIndex !== -1 && events[eventIndex].registeredCount > 0) {
      events[eventIndex].registeredCount -= 1;
      localStorage.setItem('campushub_events', JSON.stringify(events));
    }

    return { success: true, message: 'Registration cancelled successfully.' };
  },

  /**
   * Get registrations (for student's own registrations or all registrations for admin)
   * Flask endpoint: GET /api/registrations or GET /api/registrations/my
   */
  async getRegistrations(filters = {}) {
    await this._delay(100);
    let registrations = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');

    if (filters.userId) {
      registrations = registrations.filter(r => r.userId === filters.userId);
    }
    if (filters.eventId) {
      registrations = registrations.filter(r => r.eventId === filters.eventId);
    }
    if (filters.search) {
      const q = filters.search.toLowerCase();
      registrations = registrations.filter(r => 
        r.userName.toLowerCase().includes(q) ||
        r.userEmail.toLowerCase().includes(q) ||
        r.ticketCode.toLowerCase().includes(q) ||
        r.eventTitle.toLowerCase().includes(q)
      );
    }

    return registrations;
  },

  /**
   * Toggle attendance status for a registration (Admin)
   * Flask endpoint: PATCH /api/registrations/<id>/attendance
   */
  async toggleAttendance(regId) {
    let registrations = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');
    const index = registrations.findIndex(r => r.id === regId);
    if (index === -1) throw new Error('Registration not found');

    registrations[index].attended = !registrations[index].attended;
    localStorage.setItem('campushub_registrations', JSON.stringify(registrations));
    return registrations[index];
  },

  // ==========================================
  // 4. DASHBOARD STATS
  // ==========================================

  /**
   * Compute aggregate statistics
   * Flask endpoint: GET /api/dashboard/stats
   */
  async getStats() {
    const events = JSON.parse(localStorage.getItem('campushub_events') || '[]');
    const registrations = JSON.parse(localStorage.getItem('campushub_registrations') || '[]');
    const users = JSON.parse(localStorage.getItem('campushub_users') || '[]');

    const totalCapacity = events.reduce((sum, e) => sum + (e.capacity || 0), 0);
    const totalRegistered = events.reduce((sum, e) => sum + (e.registeredCount || 0), 0);

    return {
      totalEvents: events.length,
      publishedEvents: events.filter(e => e.status === 'Published').length,
      totalRegistrations: registrations.length,
      totalStudents: users.filter(u => u.role === 'student').length,
      fillRate: totalCapacity > 0 ? Math.round((totalRegistered / totalCapacity) * 100) : 0
    };
  },

  /**
   * Helper simulator for network latency
   */
  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
};
