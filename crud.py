from sqlalchemy.orm import Session
import models, schemas, security
from typing import List

#fest crud
def get_fest(db: Session, fest_id: int):
    return db.query(models.Fest).filter(models.Fest.fest_id == fest_id).first()

def create_fest(db: Session, fest: schemas.FestCreate):
    # Create an instance of the SQLAlchemy model from the Pydantic schema
    db_item = models.Fest(name = fest.name, year = fest.year)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

#user crud
def get_user_by_username(db: Session, username: str):
    """Fetches a user from the DB by their username."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Creates a new user in the DB with a hashed password."""
    hashed_password = security.get_password_hash(user.password)
    
    # Create the SQLAlchemy model instance
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        name=user.name,
        phone=user.phone,
        email=user.email,
        role=user.role.value  # Get the string value from the enum
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def check_user_credentials(db: Session, user_login: schemas.UserLogin):
    """
    Checks if a user's username and password are valid.
    Returns the user object if valid, None otherwise.
    """
    db_user: models.User = get_user_by_username(db, username=user_login.username)
    
    # Check if user exists and password is correct
    if not db_user or not security.verify_password(user_login.password, db_user.password_hash):
        return None
        
    return db_user

# --- Team and Participant CRUD (New) ---
def add_team_to_event(db: Session, team_data: schemas.TeamCreateRequest):
    """
    Creates a team, its participants, and links them all in one transaction.
    """
    
    # 1. Check if event exists and get team size limit
    db_event = get_event(db, event_id=team_data.event_id)
    if not db_event:
        raise ValueError("Event not found")
        
    # 2. Check team size
    if len(team_data.participants) > db_event.max_team_size:
        raise ValueError(f"Team size ({len(team_data.participants)}) exceeds event limit ({db_event.max_team_size})")
    
    # Use a transaction to ensure all or nothing
    try:
        # 3. Create the Team
        db_team = models.Team(team_name=team_data.team_name)
        db.add(db_team)
        db.flush()  # Use flush to get the new team_id before commit

        # 4. Create the TeamEvent link
        db_team_event = models.TeamEvent(team_id=db_team.team_id, event_id=team_data.event_id)
        db.add(db_team_event)

        created_participants = []
        
        # 5. Loop and create Participants and TeamMember links
        for p_data in team_data.participants:
            # Create participant
            db_participant = models.Participant(**p_data.model_dump())
            db.add(db_participant)
            db.flush() # Get the new participant_id

            # Create TeamMember link
            db_team_member = models.TeamMember(
                team_id=db_team.team_id, 
                participant_id=db_participant.participant_id
            )
            db.add(db_team_member)

            #try and give the participant a room
            if assign_room_to_participant(db, db_participant.participant_id) == None:
                raise ValueError("team cannot be created as no suitable room space is available")
            
            created_participants.append(db_participant)

        db.commit() # Commit all changes at once
        
        db.refresh(db_team)
        for p in created_participants:
            db.refresh(p)
            
        # Return the created objects for the response
        return {
            "db_team": db_team,
            "db_members": created_participants
        }

    except Exception as e:
        db.rollback() # Rollback all changes if any step fails
        raise e # Re-raise the exception to be handled by main.py
    
def delete_team_by_id(db: Session, team_id: int):
    """
    Deletes a team, its participants, and all associated links
    in a single transaction.
    """
    
    # Use a transaction to ensure all or nothing
    try:
        # 1. Find the team
        db_team = db.query(models.Team).filter(models.Team.team_id == team_id).first()
        if not db_team:
            raise ValueError("Team not found")

        # 2. Find all participants associated with this team
        team_members = db.query(models.TeamMember).filter(models.TeamMember.team_id == team_id).all()
        participant_ids = [tm.participant_id for tm in team_members]
        
        # 3. Find all event registrations for this team
        team_events = db.query(models.TeamEvent).filter(models.TeamEvent.team_id == team_id).all()

        # 4. Delete the links first (TeamMember and TeamEvent)
        # These reference the team and participants
        for tm in team_members:
            db.delete(tm)
            
        for te in team_events:
            db.delete(te)
            
        # --- FIX: Flush the session ---
        # This sends the DELETE commands for team_members and team_events
        # to the database immediately, *before* we proceed.
        # This resolves the foreign key violation.
        db.flush() 
        
        # 5. Delete the team itself (as requested)
        db.delete(db_team)

        for id in participant_ids:
            remove_reservation(db, id)

        # 6. Delete the participants who were on this team
        if participant_ids:
            # Delete participants based on the collected IDs
            db.query(models.Participant).filter(
                models.Participant.participant_id.in_(participant_ids)
            ).delete(synchronize_session=False)

        # 7. Commit all changes
        db.commit()
        
        return db_team # Return the deleted team object for reference

    except Exception as e:
        db.rollback() # Rollback all changes if any step fails
        raise e # Re-raise the exception to be handled by main.py
    
# --- College and Club CRUD ---

def get_college_by_name(db: Session, name: str):
    """Fetches a college by name."""
    return db.query(models.College).filter(models.College.name == name).first()

def create_college(db: Session, college: schemas.CollegeCreate):
    """Creates a new college in the DB."""
    db_college = models.College(**college.model_dump())
    db.add(db_college)
    db.commit()
    db.refresh(db_college)
    return db_college

def get_club_by_name(db: Session, name: str):
    """Fetches a club by name."""
    return db.query(models.Club).filter(models.Club.club_name == name).first() # <-- Changed from 'models.Club.name'

def create_club(db: Session, club: schemas.ClubCreate):
    """Creates a new club in the DB."""
    db_club = models.Club(**club.model_dump())
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club

#-- room crud--
def get_room_by_details(db: Session, building_name: str, room_no: str):
    """
    Fetches a room by its building name and room number to check for duplicates.
    """
    return db.query(models.Room).filter(
        models.Room.building_name == building_name,
        models.Room.room_no == room_no
    ).first()

def create_room(db: Session, room: schemas.RoomCreate):
    """
    Creates a new room in the DB AND initializes its occupancy record.
    This is now a single transaction.
    """
    try:
        # 1. Create the room
        db_room = models.Room(**room.model_dump())
        db.add(db_room)
        
        # 2. Flush the session to get the new db_room.room_id
        #    without committing the transaction yet.
        db.flush()

        # 3. Create the corresponding occupancy record
        db_occupancy = models.RoomOccupancy(
            room_id=db_room.room_id,
            current_occupancy=0  # Initialize occupancy at 0
        )
        db.add(db_occupancy)
        
        # 4. Commit both operations as a single transaction
        db.commit()
        
        # 5. Refresh the room object
        db.refresh(db_room)
        return db_room
    except Exception as e:
        db.rollback() # Rollback all changes if any step fails
        raise e # Re-raise the exception

def add_participant_to_room_reserved(db: Session, participant_id: int, room_id: int):
    """
    Creates a new entry in the RoomReserved table.
    DOES NOT COMMIT. This is intended to be used within a transaction.
    """
    db_reservation = models.RoomReserved(
        participant_id=participant_id,
        room_id=room_id
    )
    db.add(db_reservation)
    return db_reservation

def increment_room_occupancy(db: Session, room_id: int):
    """
    Finds the occupancy record for a room and increments its count.
    DOES NOT COMMIT. This is intended to be used within a transaction.
    """
    # Fetch the occupancy record
    db_occupancy = db.query(models.RoomOccupancy).filter(
        models.RoomOccupancy.room_id == room_id
    ).first()
    
    if db_occupancy:
        # Increment the count
        db_occupancy.current_occupancy += 1
        return db_occupancy
    else:
        # This should not happen if create_room is used correctly
        raise Exception(f"No RoomOccupancy record found for room_id {room_id}")
    
def decrement_room_occupancy(db: Session, room_id: int, count: int = 1):
    """
    Finds the occupancy record for a room and decrements its count.
    Ensures occupancy does not go below zero.
    DOES NOT COMMIT. This is intended to be used within a transaction.
    """
    # Fetch the occupancy record
    db_occupancy = db.query(models.RoomOccupancy).filter(
        models.RoomOccupancy.room_id == room_id
    ).first()
    
    if db_occupancy:
        # Decrement the count, ensuring it stays at 0 or above
        db_occupancy.current_occupancy = max(0, db_occupancy.current_occupancy - count)
        return db_occupancy
    else:
        # This case is problematic (data inconsistency), but we shouldn't
        # block the team deletion. We'll just return None.
        return None

def _remove_reservation_no_commit(db: Session, participant_id: int):
    """
    Internal helper: Finds and removes a participant's room reservation.
    Decrements room occupancy.
    DOES NOT COMMIT.
    """
    # 1. Find the participant's reservation
    reservation = db.query(models.RoomReserved).filter(
        models.RoomReserved.participant_id == participant_id
    ).first()
    
    if not reservation:
        # Participant has no reservation, nothing to do
        return None
        
    # 2. Get the room_id from the reservation
    room_id = reservation.room_id
    
    # 3. Delete the reservation
    db.delete(reservation)
    
    # 4. Decrement the room's occupancy (this is already a no-commit fn)
    decrement_room_occupancy(db, room_id, count=1)
    
    return reservation

def remove_reservation(db: Session, participant_id: int):
    """
    Removes a participant's room reservation and decrements occupancy.
    This function manages its own transaction (commit/rollback).
    """
    try:
        deleted_res = _remove_reservation_no_commit(db, participant_id)
        
        if deleted_res:
            db.commit()
            return deleted_res
        else:
            # No reservation found, no changes to commit or rollback
            return None
            
    except Exception as e:
        db.rollback()
        raise e

def assign_room_to_participant(db: Session, participant_id: int):
    """
    Finds the first available room for a participant based on their gender
    and available capacity, then assigns them to it.
    
    This function manages its own transaction (commit/rollback).
    
    Returns:
        - The new 'models.RoomReserved' object if successful.
        - The *existing* 'models.RoomReserved' object if participant is already assigned.
        - None if no suitable room is available.
    """
    
    # 1. Get participant details (especially gender)
    participant = db.query(models.Participant).filter(
        models.Participant.participant_id == participant_id
    ).first()
    
    if not participant:
        raise ValueError(f"Participant with id {participant_id} not found.")

    # 2. Check if participant is already assigned a room
    existing_reservation = db.query(models.RoomReserved).filter(
        models.RoomReserved.participant_id == participant_id
    ).first()
    
    if existing_reservation:
        return existing_reservation # Already assigned, do nothing

    participant_gender = participant.gender # Assumes participant model has 'gender'

    # 3. Find the first available room
    #    We join Room (for max_capacity and gender)
    #    with RoomOccupancy (for current_occupancy)
    available_room = db.query(models.Room) \
        .join(models.RoomOccupancy, models.Room.room_id == models.RoomOccupancy.room_id) \
        .filter(
            models.Room.gender == participant_gender,
            models.RoomOccupancy.current_occupancy < models.Room.max_capacity
        ) \
        .order_by(models.RoomOccupancy.current_occupancy.asc()) \
        .first() # Get the first room that's not full
    
    if not available_room:
        return None

    try:
        # Add to RoomReserved (adds to session)
        db_reservation = add_participant_to_room_reserved(
            db=db,
            participant_id=participant_id,
            room_id=available_room.room_id
        )
        
        increment_room_occupancy(db=db, room_id=available_room.room_id)
        
        db.commit()
        
        db.refresh(db_reservation)
        return db_reservation
        
    except Exception as e:
        db.rollback() # Rollback on failure
        raise e # Re-raise exception for the API layer to handle
# -- Event crud --

def get_event(db: Session, event_id: int):
    """Helper function to get an event by its ID."""
    return db.query(models.Event).filter(models.Event.event_id == event_id).first()

def get_event_by_name(db: Session, name: str):
    """Get a single event by its name."""
    return db.query(models.Event).filter(models.Event.name == name).first()

def create_event(db: Session, event: schemas.EventCreate):
    """Create a new event."""
    # Use .model_dump() instead of .dict()
    db_event = models.Event(**event.model_dump()) 
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

#--filter crud--
def get_participants_by_filters(
    db: Session, 
    college_name: str | None,
    club_id: int | None,
    gender: schemas.Gender | None,
    state: str | None,
    city: str | None,
    event_id: int | None
) -> List[models.Participant]:
    """
    Dynamically queries the Participant table based on provided filters,
    joining with College, Club, and Event tables as needed.
    """
    
    # Start with a query for all participants
    query = db.query(models.Participant)
    
    # --- Event Filter (requires multiple joins) ---
    if event_id is not None:
        # Join Participant -> TeamMember -> Team -> TeamEvent
        query = query.join(
            models.TeamMember, 
            models.Participant.participant_id == models.TeamMember.participant_id
        ).join(
            models.Team, 
            models.TeamMember.team_id == models.Team.team_id
        ).join(
            models.TeamEvent, 
            models.Team.team_id == models.TeamEvent.team_id
        )
        # Filter on the final joined table (TeamEvent)
        query = query.filter(models.TeamEvent.event_id == event_id)
        
    # --- College/State/City Filters (requires join) ---
    if college_name or state or city:
        # Join Participant -> College
        query = query.join(
            models.College, 
            models.Participant.college_id == models.College.college_id
        )
        
        if college_name:
            # Use .ilike() for case-insensitive partial matching
            query = query.filter(models.College.name.ilike(f"%{college_name}%"))
            
        if state:
            query = query.filter(models.College.state.ilike(f"%{state}%"))
            
        if city:
            query = query.filter(models.College.city.ilike(f"%{city}%"))

    # --- Club Filter (requires join) ---
    if club_id is not None:
        # Join Participant -> Club
        # We add isouter=True to make it a LEFT JOIN, in case a 
        # participant doesn't have a club_id set.
        query = query.join(
            models.Club, 
            models.Participant.club_id == models.Club.club_id,
            isouter=True 
        )
        query = query.filter(models.Club.club_id == club_id)
        
    # --- Gender Filter (direct on Participant table) ---
    if gender:
        query = query.filter(models.Participant.gender == gender)
        
    # Prevent duplicate participants if multiple joins match
    query = query.distinct()
        
    # Execute the final query and return all results
    return query.all()

def get_colleges_by_filters(db: Session, city: str | None, state: str | None) -> List[models.College]:
    """
    Dynamically queries the College table based on city and/or state.
    """
    query = db.query(models.College)
    
    if city:
        query = query.filter(models.College.city.ilike(f"%{city}%"))
        
    if state:
        query = query.filter(models.College.state.ilike(f"%{state}%"))
        
    return query.all()

def get_clubs_by_filters(db: Session, club_type: str | None) -> List[models.Club]:
    """
    Dynamically queries the Club table based on club type.
    """
    query = db.query(models.Club)
    
    if club_type:
        # Use .ilike() for case-insensitive partial matching
        query = query.filter(models.Club.club_type.ilike(f"%{club_type}%"))
        
    return query.all()