// clubs-tab.js
// Module for managing the Clubs tab

const ClubsModule = (function () {
    const API_URL = 'http://127.0.0.1:8000';
    let clubsTable;

    function init() {
        // Initialize DataTable
        clubsTable = new DataTable('#clubs-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25
        });

        const user = getStoredUser();
        const addClubButton = document.querySelector('[data-bs-target="#addClubModal"]');
        if (addClubButton) {
            if (user.role === 'Volunteer') {
                addClubButton.style.display = 'none';
            }
        }

        // Set up event listeners
        setupEventListeners();

        // Load initial data
        loadClubs();
    }

    function setupEventListeners() {
        const filterForm = document.getElementById('clubs-filter-form');
        const clearBtn = document.getElementById('club-clear-filters');

        filterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await loadClubs();
        });

        clearBtn.addEventListener('click', () => {
            filterForm.reset();
            loadClubs();
        });
    }

    async function loadClubs() {
        try {
            // Build query parameters from filter form
            const params = new URLSearchParams();

            const clubType = document.getElementById('club-type-filter').value.trim();

            if (clubType) params.append('club_type', clubType);

            const url = `${API_URL}/clubs/query/?${params.toString()}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Update table
            updateTable(data);

        } catch (error) {
            console.error('Error loading clubs:', error);
            alert('Failed to load clubs. Please try again.');
        }
    }

    function updateTable(data) {
        // Clear existing data
        clubsTable.clear();

        // Add new data
        data.forEach(club => {
            clubsTable.row.add([
                club.club_id,
                club.club_name,
                club.college_id,
                club.club_type || 'N/A',
                club.poc || 'N/A',
                club.poc_contact,
                club.poc_position || 'N/A'
            ]);
        });

        // Redraw table
        clubsTable.draw();
    }

    // Public API
    return {
        init: init,
        reload: loadClubs
    };
})();