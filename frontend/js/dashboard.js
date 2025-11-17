// dashboard.js
// Main dashboard controller - handles authentication and tab navigation

document.addEventListener('DOMContentLoaded', () => {
    
    // --- Authentication & User Info ---
    const logoutButton = document.getElementById('logout-button');
    const welcomeUser = document.getElementById('welcome-user');
    const user = getStoredUser(); // Function from auth.js

    if (user && user.name) {
        welcomeUser.textContent = `Welcome, ${user.name} (${user.role})`;
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            localStorage.removeItem('festUser');
            window.location.href = 'login.html';
        });
    }

    // --- Tab Navigation ---
    setupTabNavigation();

    // --- Initialize Modules ---
    ParticipantsModule.init();
    CollegesModule.init();
    EventsModule.init();
    AccommodationModule.init();
    ClubsModule.init();
    UsersModule.init();
});

function setupTabNavigation() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            // Add active class to clicked link
            link.classList.add('active');
            
            // Hide all tab contents
            tabContents.forEach(tab => tab.style.display = 'none');
            
            // Show selected tab
            const tabName = link.getAttribute('data-tab');
            document.getElementById(`${tabName}-tab`).style.display = 'block';
        });
    });
}