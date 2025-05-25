document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    const profileTab = document.getElementById('profile-tab');
    const securityTab = document.getElementById('security-tab');
    const profileCard = document.getElementById('profile-card');
    const securityCard = document.getElementById('security-card');
  
    profileTab.addEventListener('click', (e) => {
      e.preventDefault();
      profileTab.classList.add('active');
      securityTab.classList.remove('active');
      profileCard.style.display = 'block';
      securityCard.style.display = 'none';
    });
  
    securityTab.addEventListener('click', (e) => {
      e.preventDefault();
      securityTab.classList.add('active');
      profileTab.classList.remove('active');
      securityCard.style.display = 'block';
      profileCard.style.display = 'none';
    });
  
})