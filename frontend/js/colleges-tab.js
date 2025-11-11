// colleges-tab.js
// Module for managing the Colleges tab

const CollegesModule = (function() {
    const API_URL = 'http://127.0.0.1:8000';
    let collegesTable;

    function init() {
        // Initialize DataTable
        collegesTable = new DataTable('#colleges-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25
        });

        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        loadColleges();
    }

    function setupEventListeners() {
        const filterForm = document.getElementById('colleges-filter-form');
        const clearBtn = document.getElementById('c-clear-filters');

        filterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await loadColleges();
        });

        clearBtn.addEventListener('click', () => {
            filterForm.reset();
            loadColleges();
        });
    }

    async function loadColleges() {
        try {
            // Build query parameters from filter form
            const params = new URLSearchParams();
            
            const city = document.getElementById('c-city').value.trim();
            const state = document.getElementById('c-state').value.trim();

            if (city) params.append('city', city);
            if (state) params.append('state', state);

            const url = `${API_URL}/colleges/query/?${params.toString()}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update table
            updateTable(data);

        } catch (error) {
            console.error('Error loading colleges:', error);
            alert('Failed to load colleges. Please try again.');
        }
    }

    function updateTable(data) {
        // Clear existing data
        collegesTable.clear();
        
        // Add new data
        data.forEach(college => {
            collegesTable.row.add([
                college.college_id,
                college.name,
                college.city,
                college.state
            ]);
        });
        
        // Redraw table
        collegesTable.draw();
    }

    // Public API
    return {
        init: init,
        reload: loadColleges
    };
})();