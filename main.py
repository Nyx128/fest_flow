from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware  # Import this
from sqlalchemy.orm import Session
from typing import List
from datetime import date, time

# Import everything from your other files
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000", # Add the origin of your frontend (VSC Live Server port)
    "null" # Often needed for 'file://' origins

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- User Endpoints (New) ---

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    API endpoint to create a new user.
    """
    # Check if user with that username already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # Create the user
    return crud.create_user(db=db, user=user)

@app.post("/users/validate/", response_model=schemas.User)
def validate_user_credentials(
    user_login: schemas.UserLogin, 
    db: Session = Depends(get_db)
):
    """
    API endpoint to query/check if a username and password are valid.
    
    Returns the User object if valid, otherwise raises a 401 Unauthorized error.
    """
    db_user = crud.check_user_credentials(db, user_login=user_login)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, # Standard for 401
        )
        
    # If credentials are correct, return the user's data
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def get_all_users(db: Session = Depends(get_db)):
    """
    API endpoint to get all users.
    (In production, this should be protected with authentication middleware)
    """
    users = db.query(models.User).all()
    return users


# --- API Endpoint for fests---
@app.post("/fests/", response_model=schemas.Fest)
def create_fest_endpoint(fest: schemas.FestCreate, db: Session = Depends(get_db)):
    # Now we just call our clean CRUD function
    return crud.create_fest(db=db, fest = fest)

@app.get("/fests/{fest_id}", response_model=schemas.Fest)
def read_fest(fest_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_fest(db, fest_id=fest_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Fest not found")
    return db_item

# --- Team Endpoints ---
@app.post("/teams/add_to_event/", response_model=schemas.FullTeamResponse, status_code=status.HTTP_201_CREATED)
def add_team_to_event_endpoint(
    team_data: schemas.TeamCreateRequest, 
    db: Session = Depends(get_db)
):
    """
    Adds a new team and its participants to a specific event.
    
    This is a transactional operation:
    - Creates the Team
    - Creates all Participants
    - Links Team to Event (TeamEvent)
    - Links all Participants to Team (TeamMember)
    
    Rolls back all changes if any step fails.
    """
    try:
        result = crud.add_team_to_event(db=db, team_data=team_data)
        
        db_team = result["db_team"]
        db_members = result["db_members"]

        # Manually build the Pydantic response model
        # We can't use from_orm directly on db_team because FullTeamResponse
        # also needs 'members' and 'event_id', which aren't on the model.
        
        response = schemas.FullTeamResponse(
            team_id=db_team.team_id,
            team_name=db_team.team_name,
            event_id=team_data.event_id,
            members=[schemas.Participant.from_orm(p) for p in db_members]
        )
        return response

    except ValueError as e:
        # Handle known errors from our CRUD function
        error_str = str(e)
        if "Event not found" in error_str:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_str)
        if "Team size exceeds" in error_str:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_str)
        
        # Catch other potential validation errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_str)
    
    except Exception as e:
        # Catch any other unexpected database errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An internal error occurred: {str(e)}"
        )
    
@app.delete("/teams/{team_id}", response_model=schemas.TeamDeleteResponse)
def delete_team_endpoint(team_id: int, db: Session = Depends(get_db)):
    """
    Deletes a team and all its participants.
    
    This is a transactional operation:
    - Deletes Team
    - Deletes all Participants on the team
    - Deletes all TeamMember links
    - Deletes all TeamEvent links
    
    Rolls back all changes if any step fails.
    """
    try:
        deleted_team = crud.delete_team_by_id(db=db, team_id=team_id)
        
        return schemas.TeamDeleteResponse(
            team_id=deleted_team.team_id,
            team_name=deleted_team.team_name,
            message="Team and all associated participants deleted successfully"
        )

    except ValueError as e:
        # Handle known errors from our CRUD function
        error_str = str(e)
        if "Team not found" in error_str:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_str)
        
        # Catch other potential validation errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_str)
    
    except Exception as e:
        # Catch any other unexpected database errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An internal error occurred: {str(e)}"
        )

#--colleges and club endpoints
@app.post("/colleges/", response_model=schemas.College, status_code=status.HTTP_201_CREATED)
def create_college_endpoint(
    college: schemas.CollegeCreate, 
    db: Session = Depends(get_db)
):
    """
    API endpoint to create a new college.
    """
    db_college = crud.get_college_by_name(db, name=college.name)
    if db_college:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="College with this name already exists"
        )
    return crud.create_college(db=db, college=college)

@app.post("/clubs/", response_model=schemas.Club, status_code=status.HTTP_201_CREATED)
def create_club_endpoint(
    club: schemas.ClubCreate, 
    db: Session = Depends(get_db)
):
    """
    API endpoint to create a new club.
    """
    db_club = crud.get_club_by_name(db, name=club.club_name) # <-- Changed from 'club.name'
    if db_club:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Club with this name already exists"
        )
    return crud.create_club(db=db, club=club)

#-- rooms endpoint--
@app.post("/rooms/", response_model=schemas.Room, status_code=status.HTTP_201_CREATED)
def create_room_endpoint(
    room: schemas.RoomCreate, 
    db: Session = Depends(get_db)
):
    """
    API endpoint to create a new room.
    
    Checks for duplicates based on building_name and room_no.
    """
    # Check if a room with this building name and room number already exists
    db_room = crud.get_room_by_details(
        db, 
        building_name=room.building_name, 
        room_no=room.room_no
    )
    if db_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with this building name and room number already exists"
        )
    
    # If no duplicate, create the new room
    return crud.create_room(db=db, room=room)


#-- event endpoints--
@app.post("/events/", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
def create_event_endpoint(
    event: schemas.EventCreate, 
    db: Session = Depends(get_db)
):
    """
    API endpoint to create a new event.
    """
    # Check if event with that name already exists
    db_event = crud.get_event_by_name(db, name=event.name)
    if db_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Event with name '{event.name}' already exists"
        )
    
    # Check if the fest_id exists
    db_fest = crud.get_fest(db, fest_id=event.fest_id)
    if not db_fest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fest with fest_id {event.fest_id} not found"
        )
        
    return crud.create_event(db=db, event=event)

@app.get("/events/search/", response_model=schemas.Event)
def read_event_by_name_endpoint(
    name: str, 
    db: Session = Depends(get_db)
):
    """
    API endpoint to get a single event by its name.
    Usage: /events/search?name=EventName
    """
    # We re-use the CRUD function we already built for validation
    db_event = crud.get_event_by_name(db, name=name)
    if db_event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return db_event

@app.get("/events/{event_id}", response_model=schemas.Event)
def read_event_endpoint(event_id: int, db: Session = Depends(get_db)):
    """
    API endpoint to get a single event by its ID.
    """
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return db_event

#--filter endpoints--
@app.get("/participants/query/", response_model=List[schemas.Participant])
def query_participants(
    college_name: str | None = None,
    club_id: int | None = None,
    gender: schemas.Gender | None = None,
    state: str | None = None,
    city: str | None = None,
    event_id: int | None = None,
    db: Session = Depends(get_db)
):
    """
    API endpoint to get participants based on dynamic filters.
    Usage:
    /participants/query/
    /participants/query/?college_name=SomeCollege
    /participants/query/?event_id=10&gender=Male
    /participants/query/?club_id=5&state=SomeState
    """
    participants = crud.get_participants_by_filters(
        db, 
        college_name=college_name,
        club_id=club_id, 
        gender=gender, 
        state=state, 
        city=city,
        event_id=event_id
    )
    return participants\
    
@app.get("/events/query/", response_model=List[schemas.Event])
def query_events(
    category: schemas.CategoryEnum | None = None,
    venue: str | None = None,
    date: date | None = None, # Make sure `from datetime import date` is at the top
    db: Session = Depends(get_db)
):
    """
    API endpoint to get events based on dynamic filters.
    Usage:
    /events/query/
    /events/query/?category=technical
    /events/query/?venue=Auditorium
    """
    events = crud.get_events_by_filters(
        db, 
        category=category,
        venue=venue,
        date=date
    )
    return events

@app.get("/colleges/query/", response_model=List[schemas.College])
def query_colleges(
    city: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db)
):
    """
    API endpoint to get colleges based on city and/or state.
    (You already wrote the CRUD function for this!)
    """
    colleges = crud.get_colleges_by_filters(db, city=city, state=state)
    return colleges


@app.get("/clubs/query/", response_model=List[schemas.Club])
def query_clubs(
    club_type: schemas.CategoryEnum| None = None,
    db: Session = Depends(get_db)
):
    """
    API endpoint to get clubs based on club type.
    (You already wrote the CRUD function for this!)
    """
    clubs = crud.get_clubs_by_filters(db, club_type=club_type)
    return clubs

# --- Fetch all rooms with occupancy ---
@app.get("/rooms/occupancy/", status_code=status.HTTP_200_OK)
def get_rooms_with_occupancy(db: Session = Depends(get_db)):
    """
    Fetch all rooms with their current occupancy count.
    """
    rooms = crud.get_all_rooms_with_occupancy(db)
    return [
        {
            "room_id": room.Room.room_id,
            "building_name": room.Room.building_name,
            "room_no": room.Room.room_no,
            "gender": room.Room.gender,
            "max_capacity": room.Room.max_capacity,
            "current_occupancy": room.current_occupancy
        }
        for room in rooms
    ]


# --- Fetch participants by room ---
@app.get("/rooms/{room_id}/participants/", response_model=List[schemas.Participant])
def get_participants_in_room(room_id: int, db: Session = Depends(get_db)):
    """
    Returns all participants assigned to a specific room.
    """
    participants = crud.get_participants_by_room(db, room_id=room_id)
    if not participants:
        raise HTTPException(status_code=404, detail="No participants found in this room")
    return participants

@app.get("/events/{event_id}/teams/", status_code=status.HTTP_200_OK)
def get_teams_for_event(event_id: int, db: Session = Depends(get_db)):
    """
    Fetch all teams registered for a specific event with participant counts.
    """
    # Check if event exists
    db_event = crud.get_event(db, event_id=event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get all team_events for this event
    team_events = db.query(models.TeamEvent).filter(
        models.TeamEvent.event_id == event_id
    ).all()
    
    result = []
    for te in team_events:
        # Get the team
        team = db.query(models.Team).filter(
            models.Team.team_id == te.team_id
        ).first()
        
        # Count participants in this team
        participant_count = db.query(models.TeamMember).filter(
            models.TeamMember.team_id == te.team_id
        ).count()
        
        result.append({
            "team_id": team.team_id,
            "team_name": team.team_name,
            "participant_count": participant_count
        })
    
    return result


# --- New endpoint: Get participants for a specific team ---
@app.get("/teams/{team_id}/participants/", response_model=List[schemas.Participant])
def get_team_participants(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.team_id == team_id).first()
    if not team:
        raise ValueError("non existent/invalid team_id")

    participants = db.query(models.Participant).join(
        models.TeamMember,
        models.Participant.participant_id == models.TeamMember.participant_id
    ).filter(
        models.TeamMember.team_id == team_id
    ).all()
    
    return participants


# --- New endpoint: Get event statistics ---
@app.get("/events/{event_id}/stats/", status_code=status.HTTP_200_OK)
def get_event_stats(event_id: int, db: Session = Depends(get_db)):
    """
    Get statistics for a specific event (team count, participant count).
    """
    # Check if event exists
    db_event = crud.get_event(db, event_id=event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    team_count = db.query(models.TeamEvent).filter(
        models.TeamEvent.event_id == event_id
    ).count()
    
    # Count participants (through teams)
    participant_count = db.query(models.Participant).join(
        models.TeamMember,
        models.Participant.participant_id == models.TeamMember.participant_id
    ).join(
        models.TeamEvent,
        models.TeamMember.team_id == models.TeamEvent.team_id
    ).filter(
        models.TeamEvent.event_id == event_id
    ).distinct().count()

    return {
        "event_id": event_id,
        "team_count": team_count,
        "participant_count": participant_count
    }
