# Deploying BCC Portal on PythonAnywhere (free tier)

This guide targets a **new free PythonAnywhere account**. Free accounts have
these limits, and the deployment is built around them:

| Limit | Consequence |
|---|---|
| SQLite only (accounts created after 2026-01-15) | `DATABASE_URL` stays unset |
| MySQL only on older free accounts; Postgres is paid | See "Database choice" below |
| 512 MiB disk | Keep images on Cloudinary (already configured) |
| 100 CPU-seconds/day, 1 worker | Don't run bulk QR generation on PA |
| Outbound HTTP(S) is allowlisted | Cloudinary works; Gmail SMTP does not |
| 1 web app, no custom domain | Site lives at `https://<username>.pythonanywhere.com` |
| Web app paused ~every 30 days | Renew it from the Web tab |

---

## 1. Database choice

**Recommended: SQLite.** The database is ~3 MB with a few hundred rows and the
free plan runs a single web worker, so there are no concurrent writers.

**If your account was created before 2026-01-15**, MySQL is also available and
is a better production database. To use it:

1. Databases tab → create a MySQL database.
2. `.env` / Web tab: `DATABASE_URL=mysql://USER:PASSWORD@USER.mysql.pythonanywhere-services.com/USER$DBNAME`
3. Add `mysqlclient` to `requirements.txt` and `pip install mysqlclient`.
4. Run `python manage.py migrate`.

**Do not** plan on Neon/Supabase Postgres: direct database connections require a
paid PythonAnywhere plan. If Postgres is mandatory, use Render + Neon instead
(the project already supports `DATABASE_URL`).

---

## 2. Prepare the data locally

Run these **before** uploading the database. QR codes embed `DJANGO_BASE_URL`,
so changing the domain requires regenerating them.

```bash
# Regenerate every member QR code with the production domain
DJANGO_BASE_URL=https://<username>.pythonanywhere.com \
  python manage.py generate_qr_codes --force

# Make a consistent copy of the database
sqlite3 db.sqlite3 ".backup '/tmp/bcc_pa.sqlite3'"
```

Cards printed before this step encode the old URL and remain broken; reprint
them if they were already produced.

---

## 3. Upload the code

In a PythonAnywhere **Bash console**:

```bash
git clone https://github.com/iamshafin121/bcc_web_portal.git
cd bcc_web_portal
```

Upload `/tmp/bcc_pa.sqlite3` through the **Files** tab and save it as
`/home/<username>/bcc_web_portal/db.sqlite3`.

Create the virtualenv and install dependencies:

```bash
mkvirtualenv --python=/usr/bin/python3.13 bcc-venv
pip install -r requirements.txt
```

Django 6 requires Python 3.12+; Python 3.13 is available on the `innit` system
image.

---

## 4. Create the web app

1. **Web** tab → **Add a new web app** → **Manual configuration** → Python 3.13.
2. **Virtualenv**: `/home/<username>/.virtualenvs/bcc-venv`
3. **Source code**: `/home/<username>/bcc_web_portal`
4. **Working directory**: `/home/<username>/bcc_web_portal`

### WSGI file

Open the WSGI file linked from the Web tab and replace it with:

```python
import os
import sys

path = '/home/<username>/bcc_web_portal'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'bcc_web_portal.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Environment variables

Set these in the **Web** tab (Environment variables section). Do not upload a
`.env` file with secrets.

| Variable | Value |
|---|---|
| `DJANGO_SECRET_KEY` | output of `python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"` |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `<username>.pythonanywhere.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://<username>.pythonanywhere.com` |
| `DJANGO_BASE_URL` | `https://<username>.pythonanywhere.com` |
| `CLOUDINARY_CLOUD_NAME` | from `.env` |
| `CLOUDINARY_API_KEY` | from `.env` |
| `CLOUDINARY_API_SECRET` | from `.env` |
| `ANYMAIL_BREVO_API_KEY` | optional, enables confirmation emails |
| `DEFAULT_FROM_EMAIL` | verified sender, e.g. `"BAIUST Computer Club" <club@example.com>` |

`DJANGO_SECURE_SSL_REDIRECT` can be set to `True` later, after HTTPS is verified.

### Static and media mappings

Web tab → **Static files**:

| URL | Directory |
|---|---|
| `/static/` | `/home/<username>/bcc_web_portal/staticfiles` |
| `/media/` | `/home/<username>/bcc_web_portal/media` |

The `/media/` mapping is only used if Cloudinary is disabled.

---

## 5. Run the release commands

In a Bash console with the virtualenv active:

```bash
workon bcc-venv
cd /home/<username>/bcc_web_portal
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Then press **Reload** on the Web tab.

---

## 6. Verify

- `/` returns 200 and the CSS loads
- `/admin/` loads with styles
- `/events/` and an event detail page
- `/team/` shows Cloudinary images
- `/cse-fest-2026/` and `/cse-fest-2026/event/hackathon/`
- A member card and `/member/<uuid>/qr/`
- Submit one fest registration and confirm the email (if Anymail is configured)

Check the **error log** link on the Web tab for tracebacks.

---

## 7. Maintenance

**Renew the web app** before ~30 days pass, or it is paused.

**Back up the database** (no scheduled tasks on new free accounts):

```bash
cd /home/<username>/bcc_web_portal
sqlite3 db.sqlite3 ".backup 'backup-$(date +%F).sqlite3'"
```

Then download it from the Files tab and delete it from the server.

**Deploy an update**:

```bash
cd /home/<username>/bcc_web_portal
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then Reload. Static files **must** be re-collected whenever CSS/JS changes.

**Expired memberships**: run `python manage.py cleanup_expired_profiles --dry-run`
manually when needed.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `DisallowedHost` | Add the hostname to `DJANGO_ALLOWED_HOSTS` |
| `CSRF verification failed` | Add the site origin to `DJANGO_CSRF_TRUSTED_ORIGINS` |
| CSS/JS missing | Re-run `collectstatic`, check the `/static/` mapping |
| 500 on a page with an image | Run `collectstatic`; the manifest falls back safely, but the asset must exist |
| Emails never arrive | Free PA blocks SMTP; use `ANYMAIL_BREVO_API_KEY` |
| `database is locked` | Keep one worker; `OPTIONS['timeout']` is already set |
| Media 404s | Check Cloudinary credentials, or add the `/media/` mapping |
| QR scans to `localhost` | Regenerate with `--force` and the production `DJANGO_BASE_URL` |
