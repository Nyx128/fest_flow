// accommodation-tab.js
// Module for managing the Accommodation tab

const AccommodationModule = (function() {
    const API_URL = 'http://127.0.0.1:8000';
    let roomsTable;
    let participantsInRoomTable;
    let currentRoomId = null;

    function init() {
        // Initialize DataTables
        roomsTable = new DataTable('#rooms-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25,
            columns: [
                { data: 'room_id' },
                { data: 'building_name' },
                { data: 'room_no' },
                { data: 'gender' },
                { data: 'max_capacity' },
                { data: 'current_occupancy' },
                { 
                    data: null,
                    render: function(data, type, row) {
                        const percentage = (row.current_occupancy / row.max_capacity * 100).toFixed(0);
                        let badgeClass = 'bg-success';
                        if (percentage >= 90) {
                            badgeClass = 'bg-danger';
                        } else if (percentage >= 70) {
                            badgeClass = 'bg-warning';
                        }
                        return `<span class="badge ${badgeClass}">${percentage}%</span>`;
                    }
                },
                {
                    data: null,
                    render: function(data, type, row) {
                        return `<button class="btn btn-sm btn-primary view-room-btn" data-room-id="${row.room_id}">View Details</button>`;
                    }
                }
            ]
        });

        participantsInRoomTable = new DataTable('#participants-in-room-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25
        });

        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        loadRooms();
    }

    function setupEventListeners() {
        // Back button - return to rooms list
        document.getElementById('back-to-rooms-btn').addEventListener('click', () => {
            showRoomsList();
        });

        // View room details - using event delegation
        document.getElementById('rooms-table').addEventListener('click', (e) => {
            if (e.target.classList.contains('view-room-btn')) {
                const roomId = parseInt(e.target.getAttribute('data-room-id'));
                viewRoomDetails(roomId);
            }
        });
    }

    async function loadRooms() {
        try {
            const url = `${API_URL}/rooms/occupancy/`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update table
            updateRoomsTable(data);

        } catch (error) {
            console.error('Error loading rooms:', error);
            alert('Failed to load rooms. Please try again.');
        }
    }

    function updateRoomsTable(data) {
        // Clear existing data
        roomsTable.clear();
        
        // Add new data
        roomsTable.rows.add(data);
        
        // Redraw table
        roomsTable.draw();
    }

    async function viewRoomDetails(roomId) {
        currentRoomId = roomId;
        
        try {
            const url = `${API_URL}/rooms/${roomId}/participants/`;
            const response = await fetch(url);

            if (!response.ok) {
                if (response.status === 404) {
                    alert('No participants found in this room.');
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update the room details header
            updateRoomDetailsHeader(roomId);
            
            // Update participants table
            updateParticipantsInRoomTable(data);
            
            // Show room details view
            showRoomDetails();

        } catch (error) {
            console.error('Error loading room participants:', error);
            alert('Failed to load room participants. Please try again.');
        }
    }

    function updateRoomDetailsHeader(roomId) {
        // Find the room data from the current table
        const roomData = roomsTable.rows().data().toArray().find(r => r.room_id === roomId);
        
        if (roomData) {
            const headerElement = document.getElementById('room-details-header');
            headerElement.innerHTML = `
                <strong>Room:</strong> ${roomData.building_name} - ${roomData.room_no} 
                <span class="badge bg-secondary ms-2">${roomData.gender}</span>
                <span class="ms-3"><strong>Occupancy:</strong> ${roomData.current_occupancy} / ${roomData.max_capacity}</span>
            `;
        }
    }

    function updateParticipantsInRoomTable(data) {
        // Clear existing data
        participantsInRoomTable.clear();
        
        // Add new data
        data.forEach(participant => {
            participantsInRoomTable.row.add([
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
        participantsInRoomTable.draw();
    }

    function showRoomsList() {
        document.getElementById('rooms-list-view').style.display = 'block';
        document.getElementById('room-details-view').style.display = 'none';
    }

    function showRoomDetails() {
        document.getElementById('rooms-list-view').style.display = 'none';
        document.getElementById('room-details-view').style.display = 'block';
    }

    // Public API
    return {
        init: init,
        reload: loadRooms
    };
})();