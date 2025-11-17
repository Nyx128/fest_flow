// participants-tab.js
// Module for managing the Participants tab

const ParticipantsModule = (function() {
    const API_URL = 'http://127.0.0.1:8000';
    let participantsTable;

    function init() {
        participantsTable = new DataTable('#participants-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25
        });

        setupEventListeners();

        loadParticipants();

        loadEventsDropdown();
        loadCollegesDropdown();
        loadClubsDropdown();
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

    async function loadCollegesDropdown() {
        const selectElement = document.getElementById('p-college');
        if (!selectElement) {
            console.error('College filter dropdown "p-college" not found.');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/colleges/query`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const colleges = await response.json();

            while (selectElement.options.length > 1) {
                selectElement.remove(1);
            }
            console.log(colleges)

            if (colleges && Array.isArray(colleges)) {
                colleges.forEach(college => {
                    const option = document.createElement('option');
                    option.value = college.name; 
                    option.textContent = `${college.name}`;
                    selectElement.appendChild(option);
                });
            }

        } catch (error) {
            console.error('Error loading colleges dropdown:', error);
        }
    }

    async function loadClubsDropdown() {
        const selectElement = document.getElementById('p-club-id');
        if (!selectElement) {
            console.error('Club filter dropdown "p-club-id" not found.');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/clubs/query`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const clubs = await response.json();

            while (selectElement.options.length > 1) {
                selectElement.remove(1);
            }

            // Populate with fetched clubs
            if (clubs && Array.isArray(clubs)) {
                clubs.forEach(club => {
                    const option = document.createElement('option');
                    option.value = club.club_id;
                    option.textContent = `${club.club_name} (ID: ${club.club_id})`;
                    selectElement.appendChild(option);
                });
            }

        } catch (error) {
            console.error('Error loading clubs dropdown:', error);
        }
    }


    async function loadEventsDropdown(){
        const selectElement = document.getElementById('p-event-id');
        if (!selectElement) {
            console.error('Event filter dropdown "p-event-id" not found.');
            return;
        }

        try {
            // NOTE: Assuming your endpoint for ALL events is '/events/'
            // Change this if your API endpoint is different.
            const response = await fetch(`${API_URL}/events/query/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const events = await response.json();

            // Clear any existing options (except the first "All Events" one)
            while (selectElement.options.length > 1) {
                selectElement.remove(1);
            }

            // Populate with fetched events
            if (events && Array.isArray(events)) {
                events.forEach(event => {
                    const option = document.createElement('option');
                    option.value = event.event_id;
                    option.textContent = `${event.name} (ID: ${event.event_id})`;
                    selectElement.appendChild(option);
                });
            }

        } catch (error) {
            console.error('Error loading events dropdown:', error);
        }
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