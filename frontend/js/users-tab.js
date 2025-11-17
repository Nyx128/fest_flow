// users-tab.js
// Module for managing the Users tab (Admin only)

const UsersModule = (function() {
    const API_URL = 'http://127.0.0.1:8000';
    let usersTable;
    let addUserModal; // Variable to hold the modal instance

    function init() {
        // Check if user is admin
        const user = getStoredUser();
        if (!user || user.role !== 'Admin') {
            // Hide users tab if not admin
            const usersNavLink = document.querySelector('.nav-link[data-tab="users"]');
            if (usersNavLink) {
                usersNavLink.parentElement.style.display = 'none';
            }
            return; // Don't initialize if not admin
        }

        // Initialize DataTable
        usersTable = new DataTable('#users-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25
        });

        // Get the Bootstrap modal instance
        const addUserModalElement = document.getElementById('addUserModal');
        if (addUserModalElement) {
             addUserModal = new bootstrap.Modal(addUserModalElement);
        }

        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        loadUsers();
    }

    function setupEventListeners() {
        const addUserForm = document.getElementById('add-user-form');
        
        if (addUserForm) {
            addUserForm.addEventListener('submit', handleAddUserSubmit);
        }
    }

    async function handleAddUserSubmit(event) {
        event.preventDefault(); // Prevent default page reload
        
        const form = event.target;
        const errorMessageDiv = document.getElementById('form-error-message');
        
        // Hide any previous errors
        errorMessageDiv.classList.add('d-none');
        errorMessageDiv.textContent = '';

        // Collect data from the form
        const userData = {
            username: document.getElementById('user-username').value,
            password: document.getElementById('user-password').value,
            name: document.getElementById('user-name').value,
            email: document.getElementById('user-email').value,
            phone: document.getElementById('user-phone').value,
            role: document.getElementById('user-role').value
        };

        try {
            const response = await fetch(`${API_URL}/users/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            if (!response.ok) {
                // If we get an error, try to parse the detail message from FastAPI
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            // If successful:
            // 1. Hide the modal
            if (addUserModal) {
                addUserModal.hide();
            }
            
            // 2. Reset the form
            form.reset();
            
            // 3. Reload the users table
            loadUsers();

        } catch (error) {
            // If an error occurs, show it in the modal
            console.error('Error creating user:', error);
            errorMessageDiv.textContent = error.message;
            errorMessageDiv.classList.remove('d-none');
        }
    }

    async function loadUsers() {
        try {
            const url = `${API_URL}/users/`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update table
            updateTable(data);

        } catch (error) {
            console.error('Error loading users:', error);
            alert('Failed to load users. Please try again.');
        }
    }

    function updateTable(data) {
        // Clear existing data
        usersTable.clear();
        
        // Add new data
        data.forEach(user => {
            usersTable.row.add([
                user.user_id,
                user.username,
                user.name,
                user.email,
                user.phone,
                user.role
            ]);
        });
        
        // Redraw table
        usersTable.draw();
    }

    // Public API
    return {
        init: init,
        reload: loadUsers
    };
})();