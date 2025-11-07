from sqlalchemy.orm import Session
import models, schemas, security

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

def get_event(db: Session, event_id: int):
    """Helper function to get an event by its ID."""
    return db.query(models.Event).filter(models.Event.event_id == event_id).first()

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