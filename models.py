from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Enum, Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Fest(Base):
    __tablename__ = 'fests'
    fest_id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    year = Column(Integer, nullable= False)

class Event(Base):
    __tablename__ = 'events'
    event_id = Column(Integer, primary_key= True)
    name = Column(String, nullable= False)
    fest_id = Column(Integer, ForeignKey("fests.fest_id"))
    category = Column(
        Enum("technical", "cultural", "managerial", name="category_enum"), nullable=False)
    venue = Column(String(256))
    date = Column(Date, nullable= False)
    time = Column(Time, nullable = False)
    max_team_size = Column(Integer, nullable= False)

class College(Base):
    __tablename__ = "colleges"
    college_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    city = Column(String(100))
    state = Column(String(100))

class Club(Base):
    __tablename__ = "clubs"
    club_id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.college_id"), nullable=False)
    club_name = Column(String(100), nullable=False)
    club_type = Column(String(50))
    poc = Column(String(100))
    poc_contact = Column(String(10), nullable = False)
    poc_position = Column(String(100))

class Participant(Base):
    __tablename__ = "participants"
    participant_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15))
    email = Column(String(100))
    merch_size = Column(Enum("S", "M", "L", "XL", "XXL", name="merch_size_enum"), nullable=False)
    college_id = Column(Integer, ForeignKey("colleges.college_id"))
    club_id = Column(Integer, ForeignKey("clubs.club_id"))

class Team(Base):
    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True)
    team_name = Column(String(100), nullable=False)

class TeamMember(Base):
    __tablename__ = "team_members"
    team_id = Column(Integer, ForeignKey("teams.team_id"), primary_key=True)
    participant_id = Column(Integer, ForeignKey("participants.participant_id"), primary_key=True)

class TeamEvent(Base):
    __tablename__ = "team_events"
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable = False, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=False, primary_key = True)

    
class OrganiserEvent(Base):
    __tablename__ = "organiser_events"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    event_id = Column(Integer, ForeignKey("events.event_id"), primary_key=True)

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(15))
    email = Column(String(100))
    role = Column(Enum("Admin", "Coordinator", "Event Head", "Volunteer", name="role_enum"),nullable=False)
    

class MerchDistribution(Base):
    __tablename__ = "merch_distribution"
    participant_id = Column(Integer, ForeignKey("participants.participant_id", ondelete="CASCADE"), primary_key=True)
    distributed = Column(Boolean, default=False)
    time_of_distribution = Column(TIMESTAMP)

class Certificate(Base):
    __tablename__ = "certificates"
    certificate_id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey("participants.participant_id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=False)
    certificate_type = Column(String(50))

class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(Integer, primary_key=True)
    building_name = Column(String(100))
    room_no = Column(String(20))
    gender = Column(Enum("FEMALE", "MALE", name="gender_enum"), nullable=False)
    max_capacity = Column(Integer)

class RoomOccupancy(Base):
    __tablename__ = "room_occupancy"
    room_id = Column(Integer, ForeignKey("rooms.room_id"), primary_key=True)
    current_occupancy = Column(Integer, default=0)

class RoomReserved(Base):
    __tablename__ = "room_reserved"
    participant_id = Column(Integer, ForeignKey("participants.participant_id", ondelete="CASCADE"), primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable = False)