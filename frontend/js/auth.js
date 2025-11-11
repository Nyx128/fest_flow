/*
    Authentication Guard
    This script checks if a user is logged in *before* the page loads.
    It MUST be included in the <head> of all protected pages.
*/

// Check for login status immediately in a self-contained function
(function() {
    const festUser = localStorage.getItem('festUser');
    if (!festUser) {
        // If no user data is found in localStorage, redirect to login page
        window.location.href = 'login.html';
    }
})();


// Define a reusable function to get the stored user
function getStoredUser() {
    // Always read directly from localStorage to get the current value
    const festUserJSON = localStorage.getItem('festUser');
    
    if (!festUserJSON) {
        // This case should ideally not be hit on a protected page
        // because the guard above would have redirected.
        // But if called after logout, it will correctly return null.
        return null;
    }
    
    try {
        return JSON.parse(festUserJSON);
    } catch (e) {
        console.error("Error parsing user data, logging out.");
        localStorage.removeItem('festUser');
        window.location.href = 'login.html';
        return null;
    }
}