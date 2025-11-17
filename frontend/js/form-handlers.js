// form-handlers.js
// Handles all form submissions for adding new entities

const API_URL = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
    
    // Add College Form Handler
    document.getElementById('submit-college').addEventListener('click', async () => {
        const form = document.getElementById('add-college-form');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const collegeData = {
            name: document.getElementById('college-name').value.trim(),
            city: document.getElementById('college-city').value.trim(),
            state: document.getElementById('college-state').value.trim()
        };

        try {
            const response = await fetch(`${API_URL}/colleges/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(collegeData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add college');
            }

            const result = await response.json();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addCollegeModal'));
            modal.hide();
            
            // Reset form
            form.reset();
            
            // Show success message
            alert(`College "${result.name}" added successfully!`);
            
            // Reload colleges table
            CollegesModule.reload();

        } catch (error) {
            console.error('Error adding college:', error);
            alert(`Error: ${error.message}`);
        }
    });

    // Add Club Form Handler
    document.getElementById('submit-club').addEventListener('click', async () => {
        const form = document.getElementById('add-club-form');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const clubData = {
            club_name: document.getElementById('club-name').value.trim(),
            college_id: parseInt(document.getElementById('club-college-id').value),
            club_type: document.getElementById('club-type').value.trim() || null,
            poc: document.getElementById('club-poc').value.trim() || null,
            poc_contact: document.getElementById('club-poc-contact').value.trim(),
            poc_position: document.getElementById('club-poc-position').value.trim() || null
        };

        try {
            const response = await fetch(`${API_URL}/clubs/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(clubData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add club');
            }

            const result = await response.json();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addClubModal'));
            modal.hide();
            
            // Reset form
            form.reset();
            
            // Show success message
            alert(`Club "${result.club_name}" added successfully!`);
            
            // Reload clubs table
            ClubsModule.reload();

        } catch (error) {
            console.error('Error adding club:', error);
            alert(`Error: ${error.message}`);
        }
    });

    // Add Event Form Handler
    document.getElementById('submit-event').addEventListener('click', async () => {
        const form = document.getElementById('add-event-form');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const eventData = {
            name: document.getElementById('event-name').value.trim(),
            fest_id: parseInt(document.getElementById('event-fest-id').value),
            category: document.getElementById('event-category').value,
            venue: document.getElementById('event-venue').value.trim() || null,
            date: document.getElementById('event-date').value,
            time: document.getElementById('event-time').value,
            max_team_size: parseInt(document.getElementById('event-max-team-size').value)
        };

        try {
            const response = await fetch(`${API_URL}/events/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add event');
            }

            const result = await response.json();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addEventModal'));
            modal.hide();
            
            // Reset form
            form.reset();
            
            // Show success message
            alert(`Event "${result.name}" added successfully!`);
            
            // Reload events
            EventsModule.reload();

        } catch (error) {
            console.error('Error adding event:', error);
            alert(`Error: ${error.message}`);
        }
    });

    // Add Room Form Handler
    document.getElementById('submit-room').addEventListener('click', async () => {
        const form = document.getElementById('add-room-form');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const roomData = {
            building_name: document.getElementById('room-building').value.trim(),
            room_no: document.getElementById('room-no').value.trim(),
            gender: document.getElementById('room-gender').value,
            max_capacity: parseInt(document.getElementById('room-capacity').value)
        };

        try {
            const response = await fetch(`${API_URL}/rooms/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(roomData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add room');
            }

            const result = await response.json();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addRoomModal'));
            modal.hide();
            
            // Reset form
            form.reset();
            
            // Show success message
            alert(`Room ${result.building_name} - ${result.room_no} added successfully!`);
            
            // Reload rooms table
            AccommodationModule.reload();

        } catch (error) {
            console.error('Error adding room:', error);
            alert(`Error: ${error.message}`);
        }
    });

    // Add Team Form Handler
    let memberCount = 0;

    // Add Team Member button
    document.getElementById('add-team-member').addEventListener('click', () => {
        addTeamMemberForm();
    });

    function addTeamMemberForm() {
        memberCount++;
        const container = document.getElementById('team-members-container');
        
        const memberDiv = document.createElement('div');
        memberDiv.className = 'card mb-3 p-3';
        memberDiv.id = `member-${memberCount}`;
        memberDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">Member ${memberCount}</h6>
                <button type="button" class="btn btn-sm btn-danger" onclick="removeTeamMember(${memberCount})">Remove</button>
            </div>
            <div class="row g-2">
                <div class="col-md-6">
                    <label class="form-label">Name *</label>
                    <input type="text" class="form-control member-name" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Email *</label>
                    <input type="email" class="form-control member-email" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Phone *</label>
                    <input type="text" class="form-control member-phone" pattern="\\d{10}" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Gender *</label>
                    <select class="form-select member-gender" required>
                        <option value="">Select</option>
                        <option value="MALE">Male</option>
                        <option value="FEMALE">Female</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Merch Size *</label>
                    <select class="form-select member-merch" required>
                        <option value="">Select</option>
                        <option value="S">S</option>
                        <option value="M">M</option>
                        <option value="L">L</option>
                        <option value="XL">XL</option>
                        <option value="XXL">XXL</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">College ID *</label>
                    <input type="number" class="form-control member-college" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Club ID</label>
                    <input type="number" class="form-control member-club">
                </div>
            </div>
        `;
        
        container.appendChild(memberDiv);
    }

    // Make removeTeamMember globally accessible
    window.removeTeamMember = function(id) {
        const memberDiv = document.getElementById(`member-${id}`);
        if (memberDiv) {
            memberDiv.remove();
        }
    };

    // Submit Team button
    document.getElementById('submit-team').addEventListener('click', async () => {
        const form = document.getElementById('add-team-form');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const teamName = document.getElementById('team-name').value.trim();
        const eventId = parseInt(document.getElementById('team-event-id').value);

        // Collect all team members
        const members = [];
        const memberDivs = document.querySelectorAll('#team-members-container > .card');
        
        if (memberDivs.length === 0) {
            alert('Please add at least one team member');
            return;
        }

        memberDivs.forEach(div => {
            const member = {
                name: div.querySelector('.member-name').value.trim(),
                email: div.querySelector('.member-email').value.trim(),
                phone: div.querySelector('.member-phone').value.trim(),
                gender: div.querySelector('.member-gender').value,
                merch_size: div.querySelector('.member-merch').value,
                college_id: parseInt(div.querySelector('.member-college').value),
                club_id: div.querySelector('.member-club').value ? parseInt(div.querySelector('.member-club').value) : null
            };
            members.push(member);
        });

        const teamData = {
            team_name: teamName,
            event_id: eventId,
            participants: members
        };

        try {
            const response = await fetch(`${API_URL}/teams/add_to_event/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(teamData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add team');
            }

            const result = await response.json();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addTeamModal'));
            modal.hide();
            
            // Reset form
            form.reset();
            document.getElementById('team-members-container').innerHTML = '';
            memberCount = 0;
            
            // Show success message
            alert(`Team "${result.team_name}" added successfully with ${result.members.length} members!`);
            
            // Reload event details if we're on event details view
            if (EventsModule.currentEvent) {
                EventsModule.viewEventDetails(EventsModule.currentEvent);
            }

        } catch (error) {
            console.error('Error adding team:', error);
            alert(`Error: ${error.message}`);
        }
    });

    // When Add Team modal is opened, set the event ID
    document.getElementById('addTeamModal').addEventListener('show.bs.modal', () => {
        if (EventsModule.currentEvent) {
            document.getElementById('team-event-id').value = EventsModule.currentEvent.event_id;
        }
    });

    // Clear team members when modal is closed
    document.getElementById('addTeamModal').addEventListener('hidden.bs.modal', () => {
        document.getElementById('add-team-form').reset();
        document.getElementById('team-members-container').innerHTML = '';
        memberCount = 0;
    });
});