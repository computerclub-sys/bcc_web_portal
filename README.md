# BCC Portal

Web portal for **BAIUST Computer Club (BCC)** — a student-driven tech community platform at Bangladesh Army International University of Science & Technology. Manages club membership, digital member cards with QR codes, team roster, event management, and event registration with payment tracking.

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 6.0 / Python |
| **Database** | SQLite3 (dev), PostgreSQL (prod via `dj-database-url`) |
| **Media Storage** | Local filesystem (dev) / Cloudinary (prod) |
| **Static Files** | WhiteNoise with compression |
| **QR Codes** | `qrcode` library |
| **Frontend** | Custom CSS + migrated Tailwind CSS |
| **Deployment** | Gunicorn via Procfile (Render/Heroku-ready) |

## Features

- **Membership Card System** — Claim membership via UUID-based card + QR code; 4-year expiry
- **Registration Flow** — Members scan QR card → register account → claim profile with student info
- **Digital Member Cards** — Public-facing card page with QR-based verification
- **Event Management** — CRUD events with poster images, image galleries, and status (active/running/completed)
- **Event Registration** — Register with bKash payment or offline option; admin approve/reject flow
- **Team Roster** — Panels (Advisory, Leading, Tech, Social Media, Executive) with member profiles
- **Admin Panel** — Bulk approve/reject registrations and payments, download QR codes as ZIP, generate member profiles
- **QR Code Admin** — Mass QR code generation, per-profile preview, ZIP download of unclaimed QR cards
- **Responsive Design** — Dark mode toggle, scroll animations, mobile-first layout

## Apps

### `portal/` — Core
Models: `Profile` (membership with UUID, QR code PNG, claim/expiry), `TeamMember` (panel-ordered team roster)
Views: home, login, register, profile, profile_edit, member_card, member_claim, member_expired, team, join_guide, qr_image
Management commands: `create_member_profiles`, `generate_qr_codes`, `cleanup_expired_profiles`
Admin custom actions: download QR codes ZIP, generate bulk profiles

### `events/` — Events
Models: `Event`, `EventImage` (multi-image gallery), `EventRegistration` (with bKash/offline payment tracking)
Views: event_list (paginated), event_detail, register_event
Admin: bulk approve/reject registrations and payments

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
| `DJANGO_BASE_URL` | Base URL for QR code generation |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name (optional, for production media) |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

## Project Structure

```
bcc_portal/
├── bcc_web_portal/       # Django project config (settings, urls, wsgi, asgi)
├── portal/               # Core app — auth, profiles, membership, team
│   ├── models.py         # Profile, TeamMember
│   ├── views.py          # home, login, register, profile, member_card, etc.
│   ├── admin.py          # ProfileAdmin, TeamMemberAdmin (QR ZIP, bulk profile gen)
│   ├── urls.py           # 12 routes
│   ├── management/
│   │   └── commands/     # create_member_profiles, generate_qr_codes, cleanup_expired_profiles
│   ├── templates/
│   │   ├── portal/       # 11 HTML templates
│   │   └── admin/        # Custom admin templates
│   └── static/portal/    # CSS, images, favicon
├── events/               # Events app — events, registration, payments
│   ├── models.py         # Event, EventImage, EventRegistration
│   ├── views.py          # event_list, event_detail, register_event
│   ├── admin.py          # Bulk approve/reject registrations and payments
│   ├── urls.py           # 3 routes (events namespace)
│   └── templates/events/ # event_list.html, event_detail.html
├── media/                # Uploaded event posters, team images
├── manage.py             # Django CLI
├── requirements.txt      # Python dependencies
├── Procfile              # web: gunicorn ...
└── .env.example          # Environment variable template
```

## Management Commands

```bash
# Create pre-claimed member profiles with QR codes
python manage.py create_member_profiles 600 --prefix BCC --start 1

# Generate QR codes for any members missing them
python manage.py generate_qr_codes

# Clean up expired memberships
python manage.py cleanup_expired_profiles --dry-run
python manage.py cleanup_expired_profiles --days 30
```

## Admin

Create a superuser:

```bash
python manage.py createsuperuser
```

Custom admin features at `/admin/portal/profile/`:
- **Download QR codes as ZIP** — select profiles, action dropdown
- **Download unclaimed QR codes** — button in top toolbar
- **Generate profiles** — button in top toolbar (batch create unclaimed members)

Admin at `/admin/events/eventregistration/`:
- Bulk approve/reject registration status
- Bulk approve/reject payment status

## Session Settings

- Auto-logout on browser close
- 5-minute inactivity timeout

## Deployment

```bash
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
gunicorn bcc_web_portal.wsgi --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

The included `Procfile` is compatible with Render and Heroku.

## URL Routes

| Route | View |
|---|---|
| `/` | home |
| `/login/` | login |
| `/register/` | register (with `?member_uuid=`) |
| `/profile/` | profile |
| `/profile/edit/` | profile_edit |
| `/member/<uuid>/` | member_public_view (card/expired) |
| `/member/<uuid>/claim/` | member_claim |
| `/member/<uuid>/qr/` | qr_image (raw PNG) |
| `/logout/` | logout |
| `/team/` | team |
| `/join/` | join_guide |
| `/events/` | event_list |
| `/events/<id>/` | event_detail |
| `/events/<id>/register/` | register_event |
| `/admin/` | Django admin |

## License

All Rights Reserved. See [LICENSE](LICENSE). This software may only be used
with explicit written permission from the BAIUST university authority.
