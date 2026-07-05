"""Database seeding.

Populates the database on first run with:
    * a default admin account (admin / admin123)
    * a couple of approved staff members and one pending staff
    * several sample users
    * a set of realistic sample treks
    * some sample bookings and activity entries

Seeding is idempotent: it is skipped if an admin already exists.
"""
from datetime import date, timedelta, datetime

from app.extensions import db
from app.models import (
    Activity,
    Booking,
    BookingStatus,
    DifficultyEnum,
    PaymentStatus,
    RoleEnum,
    StaffStatus,
    Trek,
    TrekStatus,
    User,
)


def seed_database() -> None:
    """Seed the database with default data if it is empty."""
    if User.query.filter_by(role=RoleEnum.ADMIN).first():
        return  # Already seeded.

    today = date.today()

    # --- Admin -----------------------------------------------------------
    admin = User(
        full_name="Site Administrator",
        username="admin",
        email="admin@trekvault.com",
        phone="+91 90000 00000",
        role=RoleEnum.ADMIN,
        status=StaffStatus.APPROVED,
        bio="Platform administrator.",
    )
    admin.set_password("admin123")
    db.session.add(admin)

    # --- Staff -----------------------------------------------------------
    staff_members = []
    staff_seed = [
        ("Tenzing Norgay", "tenzing", "tenzing@trekvault.com", StaffStatus.APPROVED),
        ("Priya Sharma", "priya", "priya@trekvault.com", StaffStatus.APPROVED),
        ("Arjun Rana", "arjun", "arjun@trekvault.com", StaffStatus.PENDING),
    ]
    for name, uname, mail, status in staff_seed:
        s = User(
            full_name=name,
            username=uname,
            email=mail,
            phone="+91 98765 43210",
            role=RoleEnum.STAFF,
            status=status,
            bio="Certified mountain guide.",
        )
        s.set_password("staff123")
        db.session.add(s)
        staff_members.append(s)

    # --- Users -----------------------------------------------------------
    users = []
    user_seed = [
        ("Rahul Verma", "rahul", "rahul@example.com"),
        ("Sneha Iyer", "sneha", "sneha@example.com"),
        ("Vikram Singh", "vikram", "vikram@example.com"),
        ("Ananya Das", "ananya", "ananya@example.com"),
    ]
    for name, uname, mail in user_seed:
        u = User(
            full_name=name,
            username=uname,
            email=mail,
            phone="+91 91234 56789",
            role=RoleEnum.USER,
            status=StaffStatus.APPROVED,
            bio="Adventure enthusiast.",
        )
        u.set_password("user123")
        db.session.add(u)
        users.append(u)

    db.session.flush()  # assign IDs so we can reference staff for treks.

    approved_staff = [s for s in staff_members if s.status == StaffStatus.APPROVED]

    # --- Treks -----------------------------------------------------------
    trek_seed = [
        {
            "name": "Everest Base Camp",
            "location": "Nepal Himalayas",
            "difficulty": DifficultyEnum.EXTREME,
            "price": 85000,
            "duration": 14,
            "slots": 20,
            "remaining": 12,
            "status": TrekStatus.OPEN,
            "image": "everest.jpg",
            "offset": 25,
            "desc": "The ultimate Himalayan adventure. Trek through Sherpa villages, "
                    "cross glacial moraines and stand at the foot of the world's "
                    "highest peak at 5,364m.",
        },
        {
            "name": "Valley of Flowers",
            "location": "Uttarakhand, India",
            "difficulty": DifficultyEnum.MODERATE,
            "price": 18500,
            "duration": 6,
            "slots": 25,
            "remaining": 18,
            "status": TrekStatus.OPEN,
            "image": "valley-flowers.jpg",
            "offset": 12,
            "desc": "A UNESCO World Heritage site bursting with alpine blooms. "
                    "A gentle yet breathtaking monsoon trek through meadows of colour.",
        },
        {
            "name": "Roopkund Mystery Lake",
            "location": "Uttarakhand, India",
            "difficulty": DifficultyEnum.HARD,
            "price": 22000,
            "duration": 8,
            "slots": 18,
            "remaining": 4,
            "status": TrekStatus.OPEN,
            "image": "roopkund.jpg",
            "offset": 30,
            "desc": "The legendary skeleton lake at 5,029m. High-altitude ridges, "
                    "dramatic campsites and a genuine mountaineering challenge.",
        },
        {
            "name": "Hampta Pass Crossing",
            "location": "Himachal Pradesh, India",
            "difficulty": DifficultyEnum.MODERATE,
            "price": 14500,
            "duration": 5,
            "slots": 30,
            "remaining": 0,
            "status": TrekStatus.CLOSED,
            "image": "hampta.jpg",
            "offset": 8,
            "desc": "A stunning crossover trek from the lush Kullu valley to the "
                    "stark moonscape of Spiti. Dramatic scenery in a short window.",
        },
        {
            "name": "Kedarkantha Summit",
            "location": "Uttarakhand, India",
            "difficulty": DifficultyEnum.EASY,
            "price": 11000,
            "duration": 6,
            "slots": 35,
            "remaining": 22,
            "status": TrekStatus.OPEN,
            "image": "kedarkantha.jpg",
            "offset": 18,
            "desc": "The perfect winter snow trek for beginners. Pine forests, "
                    "frozen clearings and a spectacular sunrise summit at 3,800m.",
        },
        {
            "name": "Sandakphu Ridge Walk",
            "location": "West Bengal, India",
            "difficulty": DifficultyEnum.MODERATE,
            "price": 16000,
            "duration": 7,
            "slots": 24,
            "remaining": 24,
            "status": TrekStatus.DRAFT,
            "image": "sandakphu.jpg",
            "offset": 45,
            "desc": "Walk the ridge that offers views of four of the five highest "
                    "peaks on earth, including Everest and Kangchenjunga.",
        },
        {
            "name": "Chadar Frozen River",
            "location": "Ladakh, India",
            "difficulty": DifficultyEnum.EXTREME,
            "price": 34000,
            "duration": 9,
            "slots": 15,
            "remaining": 15,
            "status": TrekStatus.COMPLETED,
            "image": "chadar.jpg",
            "offset": -20,
            "desc": "Walk on the frozen Zanskar river in -25°C. One of the most "
                    "surreal and demanding treks on the planet.",
        },
        {
            "name": "Brahmatal Winter Trek",
            "location": "Uttarakhand, India",
            "difficulty": DifficultyEnum.EASY,
            "price": 12500,
            "duration": 6,
            "slots": 28,
            "remaining": 20,
            "status": TrekStatus.OPEN,
            "image": "brahmatal.jpg",
            "offset": 40,
            "desc": "A serene high-altitude lake trek with panoramic views of "
                    "Mt. Trishul and Nanda Ghunti. Ideal for a first winter summit.",
        },
    ]

    treks = []
    for i, t in enumerate(trek_seed):
        start = today + timedelta(days=t["offset"])
        trek = Trek(
            name=t["name"],
            location=t["location"],
            difficulty=t["difficulty"],
            description=t["desc"],
            price=t["price"],
            duration=t["duration"],
            start_date=start,
            end_date=start + timedelta(days=t["duration"]),
            slots=t["slots"],
            remaining_slots=t["remaining"],
            status=t["status"],
            image=t["image"],
            staff_id=approved_staff[i % len(approved_staff)].id if approved_staff else None,
        )
        db.session.add(trek)
        treks.append(trek)

    db.session.flush()

    # --- Sample bookings -------------------------------------------------
    sample_bookings = [
        (users[0], treks[0], BookingStatus.CONFIRMED),
        (users[0], treks[1], BookingStatus.CONFIRMED),
        (users[1], treks[0], BookingStatus.CONFIRMED),
        (users[1], treks[4], BookingStatus.CONFIRMED),
        (users[2], treks[2], BookingStatus.CONFIRMED),
        (users[3], treks[6], BookingStatus.COMPLETED),
        (users[2], treks[6], BookingStatus.COMPLETED),
    ]
    for u, tr, status in sample_bookings:
        pay = PaymentStatus.PAID
        b = Booking(
            user_id=u.id,
            trek_id=tr.id,
            status=status,
            payment_status=pay,
            booking_date=datetime.utcnow() - timedelta(days=3),
            remarks="",
        )
        db.session.add(b)

    # --- Sample activity feed --------------------------------------------
    activities = [
        ("System initialised the platform", "System", "bi-rocket-takeoff", "general"),
        (f"{admin.full_name} created trek 'Everest Base Camp'", admin.full_name, "bi-plus-circle", "trek"),
        (f"{users[0].full_name} booked 'Everest Base Camp'", users[0].full_name, "bi-bookmark-check", "booking"),
        (f"{users[1].full_name} registered an account", users[1].full_name, "bi-person-plus", "auth"),
        (f"{approved_staff[0].full_name} completed trek 'Chadar Frozen River'"
         if approved_staff else "Staff completed a trek",
         approved_staff[0].full_name if approved_staff else "Staff",
         "bi-flag", "trek"),
    ]
    for action, actor_name, icon, category in activities:
        db.session.add(
            Activity(action=action, actor_name=actor_name, icon=icon, category=category)
        )

    db.session.commit()
