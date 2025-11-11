document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in, if so, redirect to dashboard
    if (localStorage.getItem('festUser')) {
        window.location.href = 'dashboard.html';
    }

    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    const loginButton = loginForm.querySelector('button[type="submit"]');
    const loginText = document.getElementById('login-text');
    const loginSpinner = document.getElementById('login-spinner');

    // Assumes your FastAPI server is running on http://127.0.0.1:8000
    const API_URL = 'http://127.0.0.1:8000';

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission

        // Hide previous errors
        errorMessage.classList.add('d-none');
        errorMessage.textContent = '';

        // Show spinner
        loginText.classList.add('d-none');
        loginSpinner.classList.remove('d-none');
        loginButton.disabled = true;

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${API_URL}/users/validate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                }),
            });

            if (response.ok) {
                // Login successful
                const userData = await response.json();
                
                // Store user data in localStorage to persist session
                // Your API doesn't return a JWT, so we'll store the user object.
                // In a real app, you'd store the JWT here.
                localStorage.setItem('festUser', JSON.stringify(userData));
                
                // Redirect to the dashboard
                window.location.href = 'dashboard.html';

            } else if (response.status === 401) {
                // Invalid credentials
                const errorData = await response.json();
                showError(errorData.detail || 'Invalid username or password.');
            } else {
                // Other server errors
                showError(`Error: ${response.status} ${response.statusText}`);
            }

        } catch (error) {
            // Network errors
            console.error('Login failed:', error);
            showError('Login failed. Please check your connection or try again later.');
        } finally {
            // Hide spinner
            loginText.classList.remove('d-none');
            loginSpinner.classList.add('d-none');
            loginButton.disabled = false;
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
    }
});