<div align="center">

# 🏔️ TrekVault — Trekking Management Application

**A premium, production-quality trekking management platform built with Flask, Bootstrap 5 and SQLite.**

Book guided Himalayan expeditions, manage treks as a certified guide, and administer the entire platform — all from one beautifully designed dashboard.

`Flask` · `SQLAlchemy` · `Flask-Login` · `WTForms` · `Bootstrap 5` · `SQLite`

</div>

---

## 📑 Table of Contents

1. [Overview](#-overview)
2. [Features](#-features)
3. [Tech Stack](#-tech-stack)
4. [Requirements](#-requirements)
5. [Installation](#-installation)
6. [How to Run in VS Code](#-how-to-run-in-vs-code)
7. [How to Log In (Demo Accounts)](#-how-to-log-in-demo-accounts)
8. [Folder Structure](#-folder-structure)
9. [Screenshots](#-screenshots)
10. [Business Rules](#-business-rules)
11. [Troubleshooting](#-troubleshooting)

---

## 🌄 Overview

TrekVault is a full-stack web application that manages the entire lifecycle of trekking expeditions.
It supports **three roles** — **Admin**, **Staff (Guides)** and **Users (Trekkers)** — each with a dedicated, role-protected dashboard.

- **Trekkers** browse, filter and book treks, then manage their bookings.
- **Guides** run the treks assigned to them (open/close bookings, start & complete treks, adjust capacity, view participants).
- **Admins** create and manage treks, approve or blacklist guides, moderate users, view all bookings, and read platform-wide reports.

The application is built with clean **MVC architecture**, **Flask Blueprints**, a dedicated **service layer** for business logic, and a hand-crafted design system on top of Bootstrap 5.

---

## ✨ Features

### 🔐 Authentication & Security
- Three roles: **Admin**, **Staff**, **User**
- Secure **password hashing** (Werkzeug)
- **Role-based access control** with custom decorators (`@admin_required`, `@staff_required`, `@user_required`)
- Every route is protected
- Staff accounts are **pending until approved** by an admin
- **Blacklisted users/staff cannot log in**
- CSRF protection on all forms (Flask-WTF)

### 🛡️ Admin
- Dashboard with headline statistics (total treks, users, staff, pending staff, bookings, completed treks)
- **Create / edit / delete** treks (with image upload)
- **Approve / reject / blacklist / reinstate** staff
- **Blacklist / reinstate** users
- **Assign guides** to treks
- View users, staff, bookings, and trek details
- **Reports** — completed treks, staff activity, top trekkers, recent bookings
- **Global search** across treks, users, staff and bookings
- Recent activity feed

### 🧭 Staff (Guides)
- Dashboard with assigned treks, today's departures, upcoming treks, participant counts
- **Open / close / start / complete** treks (lifecycle transitions)
- **Update slot capacity**
- View the participant list for each assigned trek
- **Cannot modify treks that are not assigned to them** (enforced with 403)

### 🥾 Users (Trekkers)
- Dashboard with upcoming bookings, stats and recommendations
- Browse **available treks** with **search + filters** (keyword, location, difficulty, date)
- **Book** and **cancel** treks
- View **upcoming bookings** and **booking history**
- **Edit profile** & change password

### 🎨 UI / UX
- Hero landing page with glassmorphism & gradients
- Sidebar dashboard layout that feels like a real SaaS admin panel
- Split-screen login / register pages
- Statistics widgets, progress bars, status badges, empty states
- Toast-style flash messages
- Fully **responsive** (laptop, tablet, mobile)
- Custom 403 / 404 / 500 error pages

---

## 🧰 Tech Stack

| Layer      | Technology                                            |
|------------|-------------------------------------------------------|
| Backend    | Flask, Flask-SQLAlchemy, Flask-Login, WTForms, Jinja2 |
| Frontend   | HTML5, Bootstrap 5, Custom CSS, Bootstrap Icons       |
| Database   | SQLite (created programmatically)                     |
| JavaScript | Used only for UI enhancement — core works without JS  |

---

## 📋 Requirements

- **Python 3.9+** (developed & tested on Python 3.13)
- **pip** (comes with Python)
- A web browser
- (Recommended) **Visual Studio Code** with the **Python extension**

All Python dependencies are listed in [`requirements.txt`](requirements.txt):

```
Flask
Flask-SQLAlchemy
Flask-Login
Flask-WTF
WTForms
email-validator
Werkzeug
```

---

## 🚀 Installation

Open a terminal in the project folder (`trekmanager/`) and run:

### 1. Create a virtual environment (recommended)

**Windows (PowerShell / CMD):**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python run.py
```

### 4. Open in your browser
```
http://127.0.0.1:5000
```

> ✅ **The database is created and seeded automatically on first run.**
> There is no separate migration or seed command to run — just `python run.py`.

---

## 💻 How to Run in VS Code

Follow these steps to run the project inside **Visual Studio Code**:

### Step 1 — Open the project
1. Launch **VS Code**.
2. Go to **File → Open Folder…** and select the `trekmanager` folder.

### Step 2 — Install the Python extension
- Open the **Extensions** panel (`Ctrl+Shift+X`), search for **"Python"** (by Microsoft) and install it.

### Step 3 — Open a terminal
- Go to **Terminal → New Terminal** (or press `` Ctrl+` ``).

### Step 4 — Create & activate a virtual environment
In the VS Code terminal:

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> If VS Code asks *"We noticed a new virtual environment, do you want to select it for the workspace?"* — click **Yes**.
> You can also select it manually via `Ctrl+Shift+P` → **Python: Select Interpreter** → choose the one inside `./venv`.

### Step 5 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 6 — Run the app
Either:
- Type `python run.py` in the terminal, **or**
- Open `run.py` and click the **▶ Run** button in the top-right corner of VS Code.

### Step 7 — Open the app
- `Ctrl+Click` the link that appears in the terminal (`http://127.0.0.1:5000`), or paste it into your browser.

### Step 8 — Stop the server
- Press `Ctrl+C` in the terminal.

---

## 🔑 How to Log In (Demo Accounts)

Go to **`http://127.0.0.1:5000/auth/login`** and use any of the accounts below.
The demo credentials are also displayed directly on the login page for convenience.

| Role      | Username  | Password   | Access                                   |
|-----------|-----------|------------|------------------------------------------|
| **Admin** | `admin`   | `admin123` | Full platform administration             |
| **Staff** | `tenzing` | `staff123` | Guide dashboard (approved)               |
| **Staff** | `priya`   | `staff123` | Guide dashboard (approved)               |
| **Staff** | `arjun`   | `staff123` | Pending approval (shows waiting screen)  |
| **User**  | `rahul`   | `user123`  | Trekker dashboard                        |
| **User**  | `sneha`   | `user123`  | Trekker dashboard                        |
| **User**  | `vikram`  | `user123`  | Trekker dashboard                        |
| **User**  | `ananya`  | `user123`  | Trekker dashboard                        |

### 👑 Logging in as Admin (step by step)
1. Start the app (`python run.py`).
2. Visit **`http://127.0.0.1:5000/auth/login`**.
3. Enter **Username:** `admin`  and  **Password:** `admin123`.
4. Click **Sign In** — you'll land on the **Admin Dashboard**.

> ℹ️ **Admin registration is intentionally disabled.** The admin account is seeded automatically.
> New sign-ups can only register as a **Trekker** or apply as a **Guide** (pending approval).

You can also register a brand-new account at **`/auth/register`** to test the trekker or guide flows.

---

## 📁 Folder Structure

```
trekmanager/
├── run.py                     # Entry point — creates app, seeds DB, starts server
├── config.py                  # Configuration (dev / prod)
├── requirements.txt           # Python dependencies
├── README.md
├── .gitignore
│
├── instance/                  # (auto-created) SQLite database lives here
│   └── trekmanager.db
│
└── app/
    ├── __init__.py            # Application factory, blueprints, error handlers, filters
    ├── extensions.py          # db & login_manager instances
    ├── main.py                # Public / landing blueprint
    │
    ├── models/                # Database models (MVC "Model")
    │   ├── user.py            #   User + roles + staff status
    │   ├── trek.py            #   Trek + status + difficulty
    │   ├── booking.py         #   Booking + status + payment status
    │   └── activity.py        #   Activity feed log
    │
    ├── forms/                 # WTForms
    │   ├── auth_forms.py      #   Login, Register, Profile
    │   └── trek_forms.py      #   Trek, Slots, Booking, Search
    │
    ├── services/              # Business logic (service layer)
    │   ├── booking_service.py #   Book / cancel with all validations
    │   ├── trek_service.py    #   Trek CRUD + lifecycle + queries
    │   ├── activity_service.py#   Activity logging
    │   └── seed_service.py    #   Auto-seed default data
    │
    ├── utils/                 # Reusable helpers
    │   ├── decorators.py      #   Role-based access decorators
    │   └── helpers.py         #   Dashboard routing, pagination
    │
    ├── auth/                  # Auth blueprint (login/register/logout/pending)
    ├── admin/                 # Admin blueprint (routes.py)
    ├── staff/                 # Staff blueprint (routes.py)
    ├── user/                  # User blueprint (routes.py)
    │
    ├── templates/             # Jinja2 templates (MVC "View")
    │   ├── base.html
    │   ├── landing.html
    │   ├── partials/          #   Reusable layouts, macros, flashes, pagination
    │   ├── auth/              #   login / register / pending
    │   ├── admin/             #   dashboard, treks, staff, users, bookings, reports, search
    │   ├── staff/             #   dashboard, treks, trek_detail
    │   ├── user/              #   dashboard, treks, bookings, profile, trek_detail
    │   └── errors/            #   403 / 404 / 500
    │
    └── static/
        ├── css/style.css      # Custom design system
        ├── js/app.js          # UI enhancements only
        └── images/            # Trek cover images
```

---

## 📸 Screenshots

> Add screenshots of the running application here. Suggested captures:


| Page                | Description                                             |
|---------------------|---------------------------------------------------------|
| Landing Page        | Hero section with featured treks                        |
| Login / Register    | Split-screen authentication                             |
| Admin Dashboard     | Statistics widgets, activity feed, pending approvals    |
| Manage Treks        | Searchable, filterable trek table                       |
| Staff Dashboard     | Today's departures & assigned treks                     |
| User — Explore      | Trek cards with filters                                 |
| Trek Detail         | Booking box with live slot availability                 |
| Reports             | Completed treks, staff & user activity                  |

_To add a screenshot, save the image inside `app/static/images/` (e.g. `screenshot-dashboard.png`) and embed it:_

```markdown
![Admin Dashboard](app/static/images/screenshot-dashboard.png)
```

---

## ⚙️ Business Rules

These rules are enforced in the **service layer** (`app/services/`):

- ✅ **No overbooking** — a trek cannot be booked beyond its capacity.
- ✅ **No double booking** — a user cannot book the same trek twice.
- ✅ **Only OPEN treks can be booked.**
- ✅ **Slots decrease automatically** when a booking is made.
- ✅ **Cancelling a booking restores the slot** and refunds payment status.
- ✅ **Only the assigned guide can manage a trek** (others get a 403).
- ✅ **Blacklisted users/staff cannot log in.**
- ✅ **Pending staff cannot access the staff dashboard** (they see a waiting screen).
- ✅ **Completing a trek** marks all confirmed bookings as completed.

### Trek Lifecycle
```
draft ──▶ open ──▶ closed ──▶ ongoing ──▶ completed
             │                    ▲
             └────────────────────┘
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Activate your virtual environment and run `pip install -r requirements.txt`. |
| `Port 5000 is in use` | Stop the other process, or change the port in `run.py` (`app.run(port=5001)`). |
| Want to reset all data | Delete the `instance/trekmanager.db` file and restart — it will re-seed automatically. |
| Images not showing | Ensure the `app/static/images/` folder is present; a `default-trek.jpg` fallback is used otherwise. |
| Styling looks broken in an offline preview | The app uses Bootstrap via CDN — make sure you're online, or view it in a normal browser tab. |
| Login says "Invalid username or password" | Use the exact demo credentials above (e.g. `admin` / `admin123`). |

---

<div align="center">

**Built with ❤️ using Flask & Bootstrap 5**

Run it, log in as `admin` / `admin123`, and start exploring. 🏔️

</div>
