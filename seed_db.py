import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"

def post(endpoint: str, payload: dict):
    url = BASE_URL.rstrip("/") + endpoint
    r = requests.post(url, json=payload)
    try:
        j = r.json()
    except Exception:
        j = r.text
    if not r.ok:
        print(f"POST {endpoint} -> ERROR {r.status_code}: {j}")
    else:
        print(f"POST {endpoint} -> OK: {str(j)[:100]}")
    return r


# --------------------------------
#       NAME GENERATION
# --------------------------------

MALE_FIRST_NAMES = [
    "Aarav", "Vihaan", "Arjun", "Aditya", "Kabir", "Ishaan", "Rohan", "Karan",
    "Rahul", "Aryan", "Manav", "Laksh", "Reyansh", "Raj", "Parth", "Shivansh",
    "Mihir", "Raghav", "Vikram", "Aniket", "Harsh", "Kunal", "Siddharth",
    "Ritesh", "Pranav", "Tushar", "Dev", "Ansh", "Yash", "Rudra"
]

FEMALE_FIRST_NAMES = [
    "Ritika", "Isha", "Sneha", "Ananya", "Meera", "Diya", "Nisha", "Priya",
    "Aditi", "Kavya", "Sanya", "Rhea", "Neha", "Tanya", "Navya", "Nikita",
    "Aarya", "Simran", "Kriti", "Tara", "Aarohi", "Shruti", "Bhavya", "Maya",
    "Trisha", "Aishwarya", "Avantika", "Chhavi", "Rupali", "Suhani"
]

LAST_NAMES = [
    "Sharma", "Verma", "Reddy", "Patel", "Singh", "Iyer", "Gupta", "Das",
    "Nair", "Chowdhury", "Mehta", "Joshi", "Bhat", "Kapoor", "Agarwal",
    "Ghosh", "Menon", "Basu", "Tripathi", "Pandey", "Jain", "Rana",
    "Bhattacharya", "Deshmukh", "Kaur", "Yadav", "Rao", "Pillai", "Naidu"
]

def random_name(gender=None):
    if gender == "MALE":
        first = random.choice(MALE_FIRST_NAMES)
    elif gender == "FEMALE":
        first = random.choice(FEMALE_FIRST_NAMES)
    else:
        # fallback if unspecified
        first = random.choice(MALE_FIRST_NAMES + FEMALE_FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"


# --------------------------------
#       CREATION HELPERS
# --------------------------------

def create_fest():
    payload = {"name": "Infotsav", "year": 2026}
    r = post("/fests/", payload)
    r.raise_for_status()
    return r.json()["fest_id"]

def create_rooms():
    rooms = []
    for bname in ("Hostel-Main", "Hostel-Annex"):
        for i in range(1, 3):
            payload = {
                "building_name": bname,
                "room_no": f"{100+i}",
                "gender": "MALE",
                "max_capacity": 100
            }
            r = post("/rooms/", payload)
            r.raise_for_status()
            rooms.append(r.json()["room_id"])
            time.sleep(0.05)
    for bname in ("Hostel-Ladies", "Hostel-East"):
        for i in range(1, 3):
            payload = {
                "building_name": bname,
                "room_no": f"{200+i}",
                "gender": "FEMALE",
                "max_capacity": 100
            }
            r = post("/rooms/", payload)
            r.raise_for_status()
            rooms.append(r.json()["room_id"])
            time.sleep(0.05)
    return rooms

def create_colleges_and_clubs():
    colleges = [
        {"name": "Indian Institute of Technology Bombay", "city": "Mumbai", "state": "Maharashtra"},
        {"name": "Indian Institute of Technology Delhi", "city": "New Delhi", "state": "Delhi"},
        {"name": "Indian Institute of Science Bangalore", "city": "Bengaluru", "state": "Karnataka"},
        {"name": "Birla Institute of Technology and Science Pilani", "city": "Pilani", "state": "Rajasthan"},
        {"name": "National Institute of Technology Tiruchirappalli", "city": "Tiruchirappalli", "state": "Tamil Nadu"},
        {"name": "Anna University", "city": "Chennai", "state": "Tamil Nadu"},
        {"name": "Jadavpur University", "city": "Kolkata", "state": "West Bengal"},
        {"name": "Delhi Technological University", "city": "New Delhi", "state": "Delhi"},
    ]

    created_colleges = []
    created_clubs = []
    club_templates = [
        ("Coding Club", "technical"),
        ("Dance Club", "cultural"),
        ("Robotics Club", "technical"),
        ("Music Club", "cultural"),
        ("Literary Club", "managerial")
    ]

    poc_base_phone = 9000000000
    for idx, c in enumerate(colleges):
        r = post("/colleges/", c)
        r.raise_for_status()
        college_obj = r.json()
        created_colleges.append(college_obj)
        college_id = college_obj["college_id"]

        for j in range(3):
            tpl = club_templates[(idx + j) % len(club_templates)]
            suffix = random.randint(10, 99)
            base_prefix = college_obj['name'].split()[0][:10]
            club_payload = {
                "club_name": f"{tpl[0]} - {base_prefix}_{suffix}",
                "college_id": college_id,
                "poc_contact": str(poc_base_phone + idx*10 + j)[0:10],
                "club_type": tpl[1],
                "poc": random_name(random.choice(["MALE", "FEMALE"])),
                "poc_position": random.choice(["President", "Secretary", "Coordinator"])
            }
            rc = post("/clubs/", club_payload)
            rc.raise_for_status()
            created_clubs.append(rc.json())
            time.sleep(0.02)
        time.sleep(0.02)

    return created_colleges, created_clubs

def create_events(fest_id: int):
    events = {
        "callidus": ("technical", "2025-12-01", "10:00:00", 4, "Auditorium A"),
        "parivesh": ("cultural", "2025-12-02", "18:00:00", 5, "Open Stage"),
        "hackatron": ("technical", "2025-12-03", "09:00:00", 4, "Lab 1"),
        "hardwired": ("technical", "2025-12-04", "09:30:00", 4, "Hardware Lab")
    }
    created_events = {}
    for name, (category, date, time_s, max_size, venue) in events.items():
        payload = {
            "name": name,
            "fest_id": fest_id,
            "category": category,
            "venue": venue,
            "date": date,
            "time": time_s,
            "max_team_size": max_size
        }
        r = post("/events/", payload)
        r.raise_for_status()
        created_events[name] = r.json()
        time.sleep(0.02)
    return created_events

def create_teams_for_events(events, colleges, clubs):
    team_count = 12
    merch_sizes = ["S", "M", "L", "XL"]
    used_emails = set()

    for ev_name, ev in events.items():
        ev_id = ev["event_id"]
        max_size = ev["max_team_size"]
        print(f"\nCreating {team_count} teams for event {ev_name} (id={ev_id})")

        for tnum in range(1, team_count + 1):
            team_name = f"{ev_name}_team_{tnum}"
            size = random.randint(1, max_size)
            participants = []

            for i in range(size):
                gender = random.choice(["MALE", "FEMALE"])
                college = random.choice(colleges)
                club_choice = random.choice(clubs) if random.random() < 0.5 else None
                club_id = club_choice["club_id"] if club_choice else None

                name = random_name(gender)
                email = f"{name.lower().replace(' ', '.')}@example.com"
                cnt = 1
                while email in used_emails:
                    email = f"{name.lower().replace(' ', '.')}{cnt}@example.com"
                    cnt += 1
                used_emails.add(email)

                participant = {
                    "name": name,
                    "phone": f"9{random.randint(100000000, 999999999)}"[:10],
                    "email": email,
                    "merch_size": random.choice(merch_sizes),
                    "college_id": college["college_id"],
                    "club_id": club_id,
                    "gender": gender
                }
                participants.append(participant)

            payload = {"team_name": team_name, "event_id": ev_id, "participants": participants}
            r = post("/teams/add_to_event/", payload)
            if r.status_code == 201:
                print(f"  ✓ Created team {team_name} ({len(participants)} participants)")
            else:
                print(f"  ✗ Failed {team_name} -> {r.status_code} {r.text}")
            time.sleep(0.05)

# --------------------------------
#             MAIN
# --------------------------------

def main():
    print("== Seeding database ==")
    try:
        fest_id = create_fest()
        print(f"Fest created (id={fest_id})")
        create_rooms()
        colleges, clubs = create_colleges_and_clubs()
        print(f"{len(colleges)} colleges, {len(clubs)} clubs created")
        events = create_events(fest_id)
        print("Events:", list(events.keys()))
        create_teams_for_events(events, colleges, clubs)
        print("\n== Done. Seeding complete ==")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
