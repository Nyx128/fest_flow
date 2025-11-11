// participants-tab.js
// Module for managing the Participants tab

const ParticipantsModule = (function() {
    const API_URL = 'http://127.0.0.1:8000';
    let participantsTable;

    function init() {
        // Initialize DataTable
        participantsTable = new DataTable('#participants-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25
        });

        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        loadParticipants();
    }

    function setupEventListeners() {
        const filterForm = document.getElementById('participants-filter-form');
        const clearBtn = document.getElementById('p-clear-filters');

        filterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await loadParticipants();
        });

        clearBtn.addEventListener('click', () => {
            filterForm.reset();
            loadParticipants();
        });
    }

    async function loadParticipants() {
        try {
            // Build query parameters from filter form
            const params = new URLSearchParams();
            
            const collegeName = document.getElementById('p-college').value.trim();
            const clubId = document.getElementById('p-club-id').value.trim();
            const gender = document.getElementById('p-gender').value;
            const state = document.getElementById('p-state').value.trim();
            const city = document.getElementById('p-city').value.trim();
            const eventId = document.getElementById('p-event-id').value.trim();

            if (collegeName) params.append('college_name', collegeName);
            if (clubId) params.append('club_id', clubId);
            if (gender) params.append('gender', gender);
            if (state) params.append('state', state);
            if (city) params.append('city', city);
            if (eventId) params.append('event_id', eventId);

            const url = `${API_URL}/participants/query/?${params.toString()}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update table
            updateTable(data);

        } catch (error) {
            console.error('Error loading participants:', error);
            alert('Failed to load participants. Please try again.');
        }
    }

    function updateTable(data) {
        // Clear existing data
        participantsTable.clear();
        
        // Add new data
        data.forEach(participant => {
            participantsTable.row.add([
                participant.participant_id,
                participant.name,
                participant.email,
                participant.phone,
                participant.gender,
                participant.merch_size,
                participant.college_id,
                participant.club_id || 'N/A'
            ]);
        });
        
        // Redraw table
        participantsTable.draw();
    }

    // Public API
    return {
        init: init,
        reload: loadParticipants
    };
})();