/**
 * CampusHub - Profile Manager Controller
 */

async function initProfilePage() {
  auth.requireAuth();
  const currentUser = auth.getCurrentUser();

  try {
    const user = await api.getUserProfile(currentUser.id);
    renderProfileForm(user);
    setupProfileFormHandler(user.id);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderProfileForm(user) {
  // Sidebar avatar & details
  const avatarInit = document.getElementById('profile-avatar-initials');
  if (avatarInit) avatarInit.textContent = user.name ? user.name.charAt(0).toUpperCase() : 'U';

  const nameHead = document.getElementById('profile-card-name');
  if (nameHead) nameHead.textContent = user.name;

  const roleHead = document.getElementById('profile-card-role');
  if (roleHead) roleHead.textContent = `${user.role.toUpperCase()} • ${user.department}`;

  // Form Fields
  document.getElementById('prof-name-input').value = user.name || '';
  document.getElementById('prof-email-input').value = user.email || '';
  document.getElementById('prof-dept-input').value = user.department || '';
  document.getElementById('prof-rollno-input').value = user.rollNo || '';
  document.getElementById('prof-semester-input').value = user.semester || '';
  document.getElementById('prof-phone-input').value = user.phone || '';
  document.getElementById('prof-bio-input').value = user.bio || '';
}

function setupProfileFormHandler(userId) {
  const form = document.getElementById('user-profile-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const updatedData = {
      name: document.getElementById('prof-name-input').value.trim(),
      department: document.getElementById('prof-dept-input').value.trim(),
      rollNo: document.getElementById('prof-rollno-input').value.trim(),
      semester: document.getElementById('prof-semester-input').value.trim(),
      phone: document.getElementById('prof-phone-input').value.trim(),
      bio: document.getElementById('prof-bio-input').value.trim()
    };

    try {
      const updatedUser = await api.updateUserProfile(userId, updatedData);
      
      // Update local storage session
      localStorage.setItem('campushub_current_user', JSON.stringify(updatedUser));
      
      showToast('Profile updated successfully!', 'success');
      renderProfileForm(updatedUser);
      initNavbar(); // refresh navbar display name
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });
}
