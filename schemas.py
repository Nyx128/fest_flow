from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum
import re
from typing import List
from datetime import date, time

class FestBase(BaseModel):
    name: str
    year: int


class FestCreate(FestBase):
    pass


class Fest(FestBase):
    fest_id: int

    class Config:
        from_attributes = True

# --- User Schemas ---
class UserRole(str, Enum):
    ADMIN = "Admin"
    COORDINATOR = "Coordinator"
    EVENT_HEAD = "Event Head"
    VOLUNTEER = "Volunteer"

class UserBase(BaseModel):
    username: str
    name: str
    phone: str
    email: EmailStr
    role: UserRole

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str: # Removed '| None' from type hints
        # Regex for exactly 10 digits
        phone_regex = r'^\d{10}$'
        
        if not re.match(phone_regex, v):
            raise ValueError('Phone number must be exactly 10 digits')
        
        return v

class UserCreate(UserBase):
    """Schema used for creating a new user. Requires a password."""
    password: str

class User(UserBase):
    """Schema used for reading user data. Does NOT include password."""
    user_id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for the login/validation endpoint."""
    username: str
    password: str


# --- Participant, Team, and Schemas ---

class ParticipantBase(BaseModel):
    name: str
    phone: str
    email: EmailStr
    merch_size: str
    college_id: int 
    club_id: int | None = None

class ParticipantCreate(ParticipantBase):
    pass

class Participant(ParticipantBase):
    participant_id: int

    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    team_name: str

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    team_id: int

    class Config:
        from_attributes = True

class TeamCreateRequest(BaseModel):
    """
    Schema for the add_team endpoint.
    Receives team name, event ID, and a list of participants to create.
    """
    team_name: str
    event_id: int
    participants: List[ParticipantCreate]

class FullTeamResponse(Team):
    """
    Response model showing the newly created team and its members.
    """
    event_id: int
    members: List[Participant]

class TeamDeleteResponse(BaseModel):
    """
    Response model for a successful team deletion.
    """
    team_id: int
    team_name: str
    message: str


#-- College schema--
class CollegeBase(BaseModel):
    name: str
    city: str
    state: str

class CollegeCreate(CollegeBase):
    pass

class College(CollegeBase):
    college_id: int

    class Config:
        from_attributes = True

class ClubBase(BaseModel):
    club_name: str
    college_id: int
    poc_contact: str  # Added: This is required as per models.py (nullable=False)
    club_type: str | None = None # Added: Optional
    poc: str | None = None # Added: Optional
    poc_position: str | None = None # Added: Optional

    @field_validator('poc_contact')
    @classmethod
    def validate_poc_contact(cls, v: str) -> str:
        """Validates the POC's phone number is exactly 10 digits."""
        # Regex for exactly 10 digits
        phone_regex = r'^\d{10}$'
        
        if not re.match(phone_regex, v):
            raise ValueError('POC contact number must be exactly 10 digits')
        
        return v

class ClubCreate(ClubBase):
    pass

class Club(ClubBase):
    club_id: int

    class Config:
        from_attributes = True


#-- room schemas---
class RoomGender(str, Enum):
    """Enumeration for Room Gender, matching the DB."""
    FEMALE = "FEMALE"
    MALE = "MALE"

class RoomBase(BaseModel):
    """Base schema for room, defining all common fields."""
    building_name: str
    room_no: str
    gender: RoomGender
    max_capacity: int

class RoomCreate(RoomBase):
    """Schema used for creating a new room. Inherits all fields from Base."""
    pass

class Room(RoomBase):
    """Schema used for reading room data. Includes the room_id."""
    room_id: int

    class Config:
        from_attributes = True

# --- Event schema ---
class CategoryEnum(str, Enum):
    """Enumeration for event category, matching the DB."""
    technical = "technical"
    cultural = "cultural"
    managerial = "managerial"

class EventBase(BaseModel):
    name: str
    fest_id: int
    category: CategoryEnum  # Use the enum here
    venue: str | None = None
    date: date
    time: time
    max_team_size: int

class EventCreate(EventBase):
    """This schema is used when *creating* a new event"""
    pass

class Event(EventBase):
    """This schema is used when *reading* (returning) an event"""
    event_id: int



    class Config:
        from_attributes = True 