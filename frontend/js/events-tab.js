// events-tab.js
// Completely rewritten module for the new card-based Events tab

const EventsModule = (function () {
    const API_URL = 'http://127.0.0.1:8000';
    let teamMembersTable;
    let allEvents = [];
    let currentEvent = null;
    let currentTeam = null;

    function init() {
        // Initialize DataTable for team members
        teamMembersTable = new DataTable('#team-members-table', {
            paging: true,
            searching: true,
            ordering: true,
            info: true,
            pageLength: 25
        });

        const user = getStoredUser();
        const addTeamButton = document.querySelector('[data-bs-target="#addEventModal"]');
        if (addTeamButton) {
            if (user.role === 'Volunteer') {
                addTeamButton.style.display = 'none';
            }
        }

        // Set up event listeners
        setupEventListeners();

        // Load initial data
        loadEvents();
    }

    function setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-events-btn').addEventListener('click', () => {
            loadEvents();
        });

        // Back to events list
        document.getElementById('back-to-events-btn').addEventListener('click', () => {
            showEventsListView();
        });

        // Back to event details
        document.getElementById('back-to-event-btn').addEventListener('click', () => {
            if (currentEvent) {
                viewEventDetails(currentEvent);
            }
        });
    }

    async function loadEvents() {
        showLoading(true);
        try {
            // Get all events without filters
            const response = await fetch(`${API_URL}/events/query/`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const events = await response.json();
            allEvents = events;

            // Get stats for each event
            const eventsWithStats = await Promise.all(
                events.map(async (event) => {
                    try {
                        const statsResponse = await fetch(`${API_URL}/events/${event.event_id}/stats/`);
                        if (statsResponse.ok) {
                            const stats = await statsResponse.json();
                            return { ...event, ...stats };
                        }
                    } catch (error) {
                        console.error(`Error loading stats for event ${event.event_id}:`, error);
                    }
                    return { ...event, team_count: 0, participant_count: 0 };
                })
            );

            // Render events by category
            renderEventsByCategory(eventsWithStats);

        } catch (error) {
            console.error('Error loading events:', error);
            alert('Failed to load events. Please try again.');
        } finally {
            showLoading(false);
        }
    }

    function renderEventsByCategory(events) {
        // Clear all containers
        document.getElementById('technical-events-container').innerHTML = '';
        document.getElementById('cultural-events-container').innerHTML = '';
        document.getElementById('managerial-events-container').innerHTML = '';

        // Group events by category
        const technical = events.filter(e => e.category === 'technical');
        const cultural = events.filter(e => e.category === 'cultural');
        const managerial = events.filter(e => e.category === 'managerial');

        // Render each category
        if (technical.length > 0) {
            renderEventCards(technical, 'technical-events-container');
        } else {
            showEmptyState('technical-events-container', 'No technical events found');
        }

        if (cultural.length > 0) {
            renderEventCards(cultural, 'cultural-events-container');
        } else {
            showEmptyState('cultural-events-container', 'No cultural events found');
        }

        if (managerial.length > 0) {
            renderEventCards(managerial, 'managerial-events-container');
        } else {
            showEmptyState('managerial-events-container', 'No managerial events found');
        }
    }

    function renderEventCards(events, containerId) {
        const container = document.getElementById(containerId);

        events.forEach(event => {
            const card = createEventCard(event);
            container.appendChild(card);
        });
    }

    function createEventCard(event) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4';

        const card = document.createElement('div');
        card.className = 'card event-card';
        card.onclick = () => viewEventDetails(event);

        card.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${event.name}</h5>
                <div class="event-meta">
                    <div class="mb-2">
                        <span>📅 ${formatDate(event.date)}</span>
                    </div>
                    <div class="mb-2">
                        <span>🕐 ${event.time}</span>
                    </div>
                    <div class="mb-2">
                        <span>📍 ${event.venue || 'Venue TBA'}</span>
                    </div>
                </div>
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <span class="badge bg-primary">${event.team_count || 0} Teams</span>
                    <span class="badge bg-secondary">${event.participant_count || 0} Participants</span>
                </div>
            </div>
        `;

        col.appendChild(card);
        return col;
    }

    async function viewEventDetails(event) {
        currentEvent = event;

        try {
            // Update event info
            document.getElementById('event-details-title').textContent = event.name;
            document.getElementById('event-info-content').innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Category:</strong> ${capitalizeFirst(event.category)}</p>
                        <p><strong>Date:</strong> ${formatDate(event.date)}</p>
                        <p><strong>Time:</strong> ${event.time}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Venue:</strong> ${event.venue || 'TBA'}</p>
                        <p><strong>Max Team Size:</strong> ${event.max_team_size}</p>
                        <p><strong>Event ID:</strong> ${event.event_id}</p>
                    </div>
                </div>
            `;

            // Load teams for this event
            const teamsResponse = await fetch(`${API_URL}/events/${event.event_id}/teams/`);

            if (!teamsResponse.ok) {
                throw new Error(`HTTP error! status: ${teamsResponse.ok}`);
            }

            const teams = await teamsResponse.json();
            renderTeamsList(teams);

            // Show event details view
            showEventDetailsView();

        } catch (error) {
            console.error('Error loading event details:', error);
            alert('Failed to load event details. Please try again.');
        }
    }

    function renderTeamsList(teams) {
        const container = document.getElementById('teams-list-container');

        if (teams.length === 0) {
            container.innerHTML = '<p class="text-muted">No teams have registered for this event yet.</p>';
            return;
        }

        container.innerHTML = '';

        teams.forEach(team => {
            const teamItem = document.createElement('div');
            teamItem.className = 'team-item';
            teamItem.onclick = () => viewTeamDetails(team);

            teamItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="team-name">${team.team_name}</div>
                        <div class="team-count">${team.participant_count} member${team.participant_count !== 1 ? 's' : ''}</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View Members →</button>
                </div>
            `;

            container.appendChild(teamItem);
        });
    }

    async function viewTeamDetails(team) {
        currentTeam = team;

        try {
            // Update team title
            document.getElementById('team-details-title').textContent = `${team.team_name} (${team.participant_count} members)`;

            // Load team members
            const response = await fetch(`${API_URL}/teams/${team.team_id}/participants/`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const participants = await response.json();

            // Update table
            updateTeamMembersTable(participants);

            // Show team details view
            showTeamDetailsView();

        } catch (error) {
            console.error('Error loading team details:', error);
            alert('Failed to load team members. Please try again.');
        }
    }

    function updateTeamMembersTable(participants) {
        // Clear existing data
        teamMembersTable.clear();

        // Add new data
        participants.forEach(participant => {
            teamMembersTable.row.add([
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
        teamMembersTable.draw();
    }

    // View management functions
    function showEventsListView() {
        document.getElementById('events-list-view').style.display = 'block';
        document.getElementById('event-details-view').style.display = 'none';
        document.getElementById('team-details-view').style.display = 'none';
    }

    function showEventDetailsView() {
        document.getElementById('events-list-view').style.display = 'none';
        document.getElementById('event-details-view').style.display = 'block';
        document.getElementById('team-details-view').style.display = 'none';
    }

    function showTeamDetailsView() {
        document.getElementById('events-list-view').style.display = 'none';
        document.getElementById('event-details-view').style.display = 'none';
        document.getElementById('team-details-view').style.display = 'block';
    }

    function showLoading(show) {
        const loadingEl = document.getElementById('events-loading');
        const sectionsEl = document.querySelectorAll('.category-section');

        if (show) {
            loadingEl.style.display = 'flex';
            sectionsEl.forEach(el => el.style.display = 'none');
        } else {
            loadingEl.style.display = 'none';
            sectionsEl.forEach(el => el.style.display = 'block');
        }
    }

    function showEmptyState(containerId, message) {
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="col-12">
                <div class="empty-state">
                    <p>${message}</p>
                </div>
            </div>
        `;
    }

    // Helper functions
    function formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    function capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // Public API
    return {
        init: init,
        reload: loadEvents
    };
})();