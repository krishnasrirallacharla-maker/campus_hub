/**
 * CampusHub - Authentication & Session State Manager
 */

const auth = {
  /**
   * Get the current active user from session
   */
  getCurrentUser() {
    const sessionStr = localStorage.getItem('campushub_current_user');
    return sessionStr ? JSON.parse(sessionStr) : null;
  },

  /**
   * Check if any user is logged in
   */
  isLoggedIn() {
    return this.getCurrentUser() !== null;
  },

  /**
   * Check if current user is an admin
   */
  isAdmin() {
    const user = this.getCurrentUser();
    return user && user.role === 'admin';
  },

  /**
   * Login user and store session
   */
  async login(email, password) {
    const response = await api.login(email, password);
    if (response && response.user) {
      localStorage.setItem('campushub_current_user', JSON.stringify(response.user));
      return response.user;
    }
    throw new Error('Authentication failed');
  },

  /**
   * Register new user and start session
   */
  async register(userData) {
    const response = await api.register(userData);
    if (response && response.user) {
      localStorage.setItem('campushub_current_user', JSON.stringify(response.user));
      return response.user;
    }
    throw new Error('Registration failed');
  },

  /**
   * Logout user and clear session
   */
  logout() {
    localStorage.removeItem('campushub_current_user');
    window.location.href = 'index.html';
  },

  /**
   * Route Guard: Require user to be logged in
   */
  requireAuth() {
    if (!this.isLoggedIn()) {
      const currentUrl = encodeURIComponent(window.location.href);
      window.location.href = `login.html?redirect=${currentUrl}`;
    }
  },

  /**
   * Route Guard: Require user to be an Admin
   */
  requireAdmin() {
    if (!this.isLoggedIn()) {
      window.location.href = 'login.html?redirect=' + encodeURIComponent(window.location.href);
      return;
    }
    if (!this.isAdmin()) {
      alert('Access Denied: Admin privileges required.');
      window.location.href = 'student-dashboard.html';
    }
  }
};
