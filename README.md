# BCC Portal

Web portal for **BAIUST Computer Club (BCC)** — Bangladesh Army International University of Science & Technology. Manages club membership, digital member cards with QR codes, team roster, club events, and CSE Spring Fest registration with payment tracking.

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 6.0 / Python |
| **Database** | SQLite3 (dev), PostgreSQL (prod via `dj-database-url`) |
| **Media Storage** | Local filesystem (dev) / Cloudinary (prod) |
| **Static Files** | WhiteNoise with compression |
| **QR Codes** | `qrcode` library |
| **Frontend** | Custom CSS + Tailwind CSS (migrated from Next.js) |
| **Email** | SMTP (Gmail) / console backend |
| **Deployment** | Gunicorn via Procfile (Render/Heroku-ready) |

## Features

### Core Portal (`portal/`)
- **Membership Card System** — UUID-based member cards with QR codes; 4-year expiry
- **Registration Flow** — Scan QR card → register account → claim profile with student info
- **Digital Member Cards** — Public card page with QR-based verification
- **Team Roster** — Panels (Advisory, Leading, Tech, Social Media, Executive) with member profiles
- **QR Code Admin** — Mass QR generation, per-profile preview, ZIP download of claimed & unclaimed QR cards
- **Profile Management** — Edit student info, phone, department, batch

### Club Events (`events/`)
- **Event CRUD** — Posters, image galleries, status (active/running/completed)
- **Event Registration** — bKash or offline payment; admin approve/reject flow
- **Bulk Admin Actions** — Approve/reject registrations and payments in bulk

### CSE Spring Fest (`cse_fest/`)
- **Fest Management** — Year-based fests with countdown, posters, bKash number
- **Fest Events** — Hackathon, IUPC, E-Football, ICT Quiz with per-event registration fees, prize pools, rule books, team management
- **Team Registration** — Multi-member team support (hackathon up to 4, IUPC up to 3) with duplicate detection
- **Payment Tracking** — bKash / physical payment per registration
- **Schedule** — Per-fest schedule with event association
- **Committee** — Organizing committee, problem setters, volunteers
- **Sponsors** — Tiered sponsors (University Partner, Tech Partner, Gold, Silver)
- **Notices & FAQs** — Per-fest notices and FAQs
- **Invitation Page** — Digital invitation landing page
- **Application Status** — Search by application ID or team name; filter confirmed team lists by category
- **Auto Email** — Confirmation email on registration; approval notification on status change
- **Excel Export** — Export approved registrations per event to `.xlsx`
- **Theme Colors** — Auto-extracted dominant colors from event posters
- **Admin Tools** — Bulk delete pending/cancelled registrations

## Apps

### `portal/` — Core
- **Models**: `Profile` (UUID membership, QR code PNG, claim/expiry), `TeamMember` (panel-ordered roster)
- **Views**: home, login, register, profile, profile_edit, member_card, member_claim, member_expired, team, join_guide, qr_image
- **Middleware**: `SuperuserSessionMiddleware` (superusers get 1-year session, others get browser-session)
- **Management**: `create_member_profiles`, `generate_qr_codes`, `cleanup_expired_profiles`
- **Templatetags**: `cloudinary_tags` (`cl_thumb` filter for Cloudinary thumbnails)

### `events/` — Club Events
- **Models**: `Event`, `EventImage`, `EventRegistration` (bKash/offline payment)
- **Views**: event_list (paginated), event_detail, register_event

### `cse_fest/` — CSE Spring Fest
- **Models**: `Fest`, `FestEvent`, `FestPrize`, `FestSchedule`, `Notice`, `CommitteeMember`, `Faq`, `Sponsor`, `FestRegistration`, `FestTeamMember`
- **Views**: index, schedule, event_detail, register (with TeamMember creation), application_status, invitation, export_approved_excel, delete_pending_cancelled
- **Admin**: `FestAdmin` with inlines (events, schedules, notices), custom registration admin with team member inline, per-fest action buttons
- **Management**: `backfill_event_colors`, `debug_colors`
- **Signals**: Auto-send confirmation email on registration approval
- **Templates**: 7 HTML templates including email template

## Quick Start

```bash
git clone <repo-url>
cd bcc_portal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (required in production) |
| `DJANGO_DEBUG` | Set `True` for development |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins |
| `DJANGO_BASE_URL` | Base URL for QR code generation & email links |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name (optional, for production media) |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `EMAIL_HOST_USER` | SMTP email (optional, falls back to console) |
| `EMAIL_HOST_PASSWORD` | SMTP password |
| `RENDER` | Set by Render platform for auto host detection |

## Project Structure

```
bcc_portal/
├── bcc_web_portal/           # Django project config
│   ├── settings.py           # Installed apps, middleware, DB, Cloudinary, email
│   ├── urls.py               # Root URL routing
│   ├── storage.py            # Custom NoCompressCloudinaryStorage
│   ├── wsgi.py / asgi.py     # WSGI & ASGI entry points
├── portal/                   # Core app — auth, profiles, membership, team
│   ├── models.py             # Profile, TeamMember
│   ├── views.py              # 12 views
│   ├── admin.py              # ProfileAdmin, TeamMemberAdmin (QR ZIP, bulk profile gen)
│   ├── urls.py               # 12 routes
│   ├── middleware.py          # SuperuserSessionMiddleware
│   ├── templatetags/         # cloudinary_tags (cl_thumb filter)
│   ├── management/commands/  # create_member_profiles, generate_qr_codes, cleanup_expired_profiles
│   ├── templates/portal/     # 11 HTML templates
│   ├── templates/admin/      # Custom admin templates
│   └── static/portal/        # CSS, images, lottie animations, SVG icons
├── events/                   # Club events app
│   ├── models.py             # Event, EventImage, EventRegistration
│   ├── views.py              # event_list, event_detail, register_event
│   ├── admin.py              # Bulk approve/reject
│   ├── urls.py               # 3 routes
│   └── templates/events/     # event_list.html, event_detail.html
├── cse_fest/                 # CSE Spring Fest app
│   ├── models.py             # Fest, FestEvent, FestPrize, FestSchedule, Notice,
│   │                         # CommitteeMember, Faq, Sponsor, FestRegistration, FestTeamMember
│   ├── views.py              # index, schedule, event_detail, register,
│   │                         # application_status, invitation, export_excel
│   ├── admin.py              # FestAdmin, registration admin with team inline
│   ├── urls.py               # 8 routes (cse_fest namespace)
│   ├── signals.py            # Auto email on registration approval
│   ├── management/commands/  # backfill_event_colors, debug_colors
│   ├── templates/cse_fest/   # 7 HTML templates + email template
│   └── static/cse_fest/      # CSS, JS (hero-bg, fire-speckles, invitation)
├── media/                    # Uploaded posters, team images, fest images
├── manage.py                 # Django CLI
├── requirements.txt          # Python dependencies
├── Procfile                  # web: gunicorn ...
├── .env.example              # Environment variable template
└── LICENSE                   # All Rights Reserved
```

## Management Commands

```bash
# Portal
python manage.py create_member_profiles 600 --prefix BCC --start 1
python manage.py generate_qr_codes
python manage.py cleanup_expired_profiles --dry-run
python manage.py cleanup_expired_profiles --days 30

# CSE Fest
python manage.py backfill_event_colors
python manage.py debug_colors
```

## Admin

```bash
python manage.py createsuperuser
```

### `/admin/portal/profile/`
- **Download QR codes as ZIP** — select profiles, action dropdown
- **Download unclaimed QR codes** — top toolbar button
- **Generate profiles** — top toolbar button (batch create unclaimed members)

### `/admin/events/eventregistration/`
- Bulk approve/reject registration status
- Bulk approve/reject payment status

### `/admin/cse_fest/festregistration/`
- Per-fest action buttons in changelist
- Team member inline (read-only)
- Search by name, email, phone, application ID, transaction ID

### `/admin/cse_fest/`
- Fest admin with inline events, schedules, notices
- FestEvent admin with inline prizes, color fields
- Notice admin with bulk activate/deactivate
- Full CRUD for Committee, FAQ, Sponsor

## URL Routes

| Route | View | App |
|---|---|---|
| `/` | home | portal |
| `/login/` | login | portal |
| `/register/` | register (`?member_uuid=`) | portal |
| `/profile/` | profile | portal |
| `/profile/edit/` | profile_edit | portal |
| `/member/<uuid>/` | member_public | portal |
| `/member/<uuid>/claim/` | member_claim | portal |
| `/member/<uuid>/qr/` | qr_image (raw PNG) | portal |
| `/logout/` | logout | portal |
| `/team/` | team | portal |
| `/join/` | join_guide | portal |
| `/events/` | event_list | events |
| `/events/<id>/` | event_detail | events |
| `/events/<id>/register/` | register_event | events |
| `/cse-fest/` | redirect_to_latest | cse_fest |
| `/cse-fest-<year>/` | index | cse_fest |
| `/cse-fest-<year>/schedule/` | schedule_view | cse_fest |
| `/cse-fest-<year>/event/<slug>/` | event_detail | cse_fest |
| `/cse-fest-<year>/register/` | register | cse_fest |
| `/cse-fest-<year>/application-status/` | application_status | cse_fest |
| `/cse-fest-<year>/invitation/` | invitation | cse_fest |
| `/cse-fest-<year>/export-approved/` | export_approved_excel | cse_fest |
| `/cse-fest-<year>/delete-pending-cancelled/` | delete_pending_cancelled | cse_fest |
| `/admin/` | Django admin | — |

## Session Settings

- Superusers: 1-year session expiry
- Regular users: browser-session (expires on browser close)
- CSRF stored in sessions (`CSRF_USE_SESSIONS = True`)

## Deployment

```bash
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
gunicorn bcc_web_portal.wsgi --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

The included `Procfile` is compatible with Render and Heroku.

## License

All Rights Reserved. See [LICENSE](LICENSE). This software may only be used
with explicit written permission from the BAIUST university authority.
