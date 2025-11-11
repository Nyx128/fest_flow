// events-tab.js
// Module for managing the Events tab

const EventsModule = (function() {
    const API_URL = 'http://127.0.0.1:8000';
    let eventsTable;

    function init() {
        // Initialize DataTable
        eventsTable = new DataTable('#events-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25
        });

        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        loadEvents();
    }

    function setupEventListeners() {
        const filterForm = document.getElementById('events-filter-form');
        const clearBtn = document.getElementById('e-clear-filters');

        filterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await loadEvents();
        });

        clearBtn.addEventListener('click', () => {
            filterForm.reset();
            loadEvents();
        });
    }

    async function loadEvents() {
        try {
            // Build query parameters from filter form
            const params = new URLSearchParams();
            
            const category = document.getElementById('e-category').value;
            const venue = document.getElementById('e-venue').value.trim();
            const date = document.getElementById('e-date').value;

            if (category) params.append('category', category);
            if (venue) params.append('venue', venue);
            if (date) params.append('date', date);

            const url = `${API_URL}/events/query/?${params.toString()}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update table
            updateTable(data);

        } catch (error) {
            console.error('Error loading events:', error);
            alert('Failed to load events. Please try again.');
        }
    }

    function updateTable(data) {
        // Clear existing data
        eventsTable.clear();
        
        // Add new data
        data.forEach(event => {
            eventsTable.row.add([
                event.event_id,
                event.name,
                event.fest_id,
                event.category,
                event.venue || 'N/A',
                event.date,
                event.time,
                event.max_team_size
            ]);
        });
        
        // Redraw table
        eventsTable.draw();
    }

    // Public API
    return {
        init: init,
        reload: loadEvents
    };
})();