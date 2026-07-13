# Online Voting System — Flask Edition

A full-stack voting web app built with **Flask** (Python) + **SQLite** + Jinja
templates. No JavaScript framework needed — everything runs from the Python
backend.

## What's included

- **Home page** — Login / Sign Up buttons
- **Sign Up** — new voters register with name, PIN, password → OTP sent (shown
  on-screen in this demo) → account is `pending` until admin approval
- **Login** — separate from admin login; blocked until OTP is verified
- **Forgot Password** — voters can reset their password via an emailed reset
  code (`/forgot-password` → `/reset-password`), independent of the sign-up OTP
- **Voter Dashboard** — shows approval status + notifications from the admin
- **Voting page** — only accessible to *approved* voters, only during the
  admin-declared voting window, and only once per voter
- **Results page** — public: winner announcement, total registered
  candidates/voters, and votes per candidate
- **Admin Login** — completely separate credentials from voters
- **Admin Dashboard / Administration** — admin can:
  - Accept or reject pending voter requests (voter gets a notification either way)
  - Register candidates as **Leader** or **CR**, in separate sections
  - Set the voting start/end date & time
- Voters have **no access** to any `/admin/...` route; admins have no ballot access
- **Fully responsive** — adapts to phones, tablets, and desktops, including
  separate handling for **portrait vs. landscape** orientation (landscape
  phones get a more compact vertical layout so nothing gets cut off on a short screen)

---

## Part 1 — Run it in VS Code (step by step)

### 1. Install prerequisites (one-time)
- **Python 3.10+** — https://www.python.org/downloads/ (on Windows, tick "Add
  Python to PATH" during install)
- **VS Code** — https://code.visualstudio.com/
- **Git** — https://git-scm.com/downloads
- In VS Code, install the **Python extension** (Microsoft) from the Extensions
  panel (left sidebar, square-ish icon).

### 2. Open the project
1. Unzip the project folder you downloaded (`flask-voting-system`).
2. Open VS Code → `File > Open Folder...` → select the `flask-voting-system` folder.

### 3. Create a virtual environment
Open a terminal in VS Code: `Terminal > New Terminal`. Then run:

```bash
python -m venv venv
```

Activate it:
- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Windows (cmd):** `venv\Scripts\activate.bat`
- **Mac/Linux:** `source venv/bin/activate`

You'll see `(venv)` appear at the start of your terminal prompt once it's active.
VS Code may also prompt "Select Interpreter" — pick the one inside `venv`.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the app

```bash
python app.py
```

You should see something like:
```
[setup] Created default admin -> username: admin  password: admin123
 * Running on http://127.0.0.1:5000
```

Open **http://127.0.0.1:5000** in your browser. That's it — the SQLite
database (`instance/voting.db`) is created automatically on first run.

### 6. Try the full flow
1. Go to **Sign Up**, register a voter (note the OTP shown in the flash message).
2. Go to **Verify OTP**, enter it.
3. Log in as admin at **/admin/login** with `admin` / `admin123`.
4. In **Voter Requests**, Accept the new voter.
5. In **Candidates**, add a few Leader and CR candidates.
6. In **Schedule**, set a voting window that includes right now (so status = `open`).
7. Log out of admin, log in as the voter, go to **Dashboard → Ballot**, vote.
8. Visit **/results** to see the tally.

> **About the OTP:** by default (no email configured) this project shows the
> OTP directly on screen. To send *real* emails instead, see the **"OTP Email
> Setup"** section below — it takes about 5 minutes with a free Gmail account.

---

## OTP Email Setup (send real OTPs instead of on-screen demo mode)

This uses **Flask-Mail** with Gmail's free SMTP server. You don't need to buy
anything — just a Gmail account and a generated "App Password."

### 1. Turn on 2-Step Verification for your Gmail account
Real Gmail App Passwords only work if 2-Step Verification is enabled.
Go to https://myaccount.google.com/security → **2-Step Verification** → turn it on
(you'll verify with your phone).

### 2. Generate an App Password
1. Go to https://myaccount.google.com/apppasswords (you may need to search
   "App Passwords" in your Google Account settings if the link doesn't work directly).
2. Under "Select app," choose **Other (Custom name)** and type e.g. `Voting System`.
3. Click **Generate**. Google shows a 16-character password like `abcd efgh ijkl mnop`.
4. Copy it (remove the spaces) — this is your `MAIL_PASSWORD`, **not** your normal Gmail password.

### 3. Add your credentials to the project
1. In the project folder, copy `.env.example` to a new file named `.env`:
   ```bash
   cp .env.example .env        # Mac/Linux
   copy .env.example .env      # Windows
   ```
2. Open `.env` in VS Code and fill in:
   ```env
   MAIL_USERNAME=youraddress@gmail.com
   MAIL_PASSWORD=abcdefghijklmnop
   MAIL_DEFAULT_SENDER=youraddress@gmail.com
   ```
   `.env` is already in `.gitignore`, so these secrets never get pushed to GitHub.

### 4. Restart the app
```bash
python app.py
```
Sign up with a real email address you can check — you should receive an actual
email with your 6-digit OTP within a few seconds. If `MAIL_USERNAME`/`MAIL_PASSWORD`
aren't set, the app automatically falls back to showing the OTP on-screen, so it
never breaks even if email isn't configured yet.

### Deploying with email working
Whichever host you use (Render, PythonAnywhere, etc.), add the same variables
(`MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, `SECRET_KEY`,
`ADMIN_USERNAME`, `ADMIN_PASSWORD`) in that platform's **Environment Variables**
settings — the same way you'd set `SECRET_KEY` in the Render steps below.

### Alternative: using a different email provider
Gmail is easiest for students, but any SMTP provider works — just change
`MAIL_SERVER`/`MAIL_PORT` in `.env` (e.g. Outlook: `smtp-mail.outlook.com`,
port `587`). For higher-volume production use, a transactional email service
like SendGrid or Mailgun (both have free tiers) is more reliable than personal
Gmail SMTP.



## Part 2 — Push it to GitHub (as a group project)

### 1. Create the repository on GitHub
1. Go to https://github.com → **New repository**.
2. Name it (e.g. `online-voting-system`), keep it **empty** (no README/license —
   we already have our own files), and click **Create repository**.
3. Copy the repo URL, e.g. `https://github.com/your-username/online-voting-system.git`

### 2. Push your local project
In the VS Code terminal (inside `flask-voting-system`):

```bash
git init
git add .
git commit -m "Initial commit: Flask online voting system"
git branch -M main
git remote add origin https://github.com/your-username/online-voting-system.git
git push -u origin main
```

`instance/voting.db` and `venv/` are already excluded via `.gitignore`, so your
database and virtual environment won't be pushed (each teammate gets a clean copy).

### 3. Add your teammates
- On GitHub: repo → **Settings > Collaborators** → **Add people** → enter their
  GitHub usernames/emails.
- Each teammate then runs:
  ```bash
  git clone https://github.com/your-username/online-voting-system.git
  cd online-voting-system
  python -m venv venv
  # activate venv (see step 3 above)
  pip install -r requirements.txt
  python app.py
  ```

### 4. A simple group workflow
To avoid overwriting each other's work, agree on a simple branch pattern:

```bash
git checkout -b feature/candidate-page      # create your own branch
# ...make changes...
git add .
git commit -m "Add candidate photo support"
git push -u origin feature/candidate-page
```

Then open a **Pull Request** on GitHub from your branch into `main`, and have a
teammate review/merge it. This keeps `main` always in a working state.

---

## Part 3 — Deploy it online (free options)

### Option A: Render.com (recommended, free tier)
1. Push your project to GitHub (Part 2).
2. Go to https://render.com → sign up (can use GitHub login) → **New +** →
   **Web Service**.
3. Connect your GitHub repo.
4. Fill in:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (already provided in the `Procfile`)
5. Add an environment variable `SECRET_KEY` with a long random string
   (Render → your service → **Environment**).
6. Click **Create Web Service**. Render builds and gives you a live URL like
   `https://online-voting-system.onrender.com`.

> **Note on the database:** by default this uses SQLite, and Render's free
> tier disks are *ephemeral* — your data can reset on redeploys/restarts/sleep
> cycles. For voter/candidate data that needs to survive permanently, follow
> the **"Persistent Database"** section right below, *before* or *after*
> creating your web service (either order works).

## Persistent Database Setup (so registered voters/candidates never get wiped)

The code already supports this — it reads a `DATABASE_URL` environment
variable and uses Postgres automatically if one is set, falling back to the
local SQLite file only when it isn't. You just need to create the database
and point the app at it.

### 1. Create a free Postgres database on Render
1. Render dashboard → **New +** → **PostgreSQL**.
2. Give it a name (e.g. `voting-db`), pick the free plan, click **Create Database**.
3. Once it's ready, open it and copy the **"Internal Database URL"** (starts
   with `postgres://...`) — use the *internal* one if your web service is
   also on Render (faster, no extra cost); use the *external* one if
   connecting from your own machine or a different host.

### 2. Point your web service at it
1. Go to your Web Service → **Environment**.
2. Add a new environment variable:
   ```
   DATABASE_URL = <paste the Internal Database URL here>
   ```
3. Save changes — Render will automatically redeploy.

### 3. That's it
On the next deploy, `db.create_all()` runs against Postgres instead of
SQLite, and your admin, voters, candidates, and notifications now live in a
real persistent database that survives redeploys and sleep cycles.

> **Free tier note:** Render's free Postgres databases expire after a set
> period (check Render's current pricing page for the exact number of days)
> and need to be recreated/reconnected afterward. For a semester-long class
> project this is usually fine; for something you need indefinitely, a paid
> Postgres instance (still cheap) removes that expiry.

### Using this locally too (optional)
If you want your local development setup to also use Postgres instead of
SQLite (e.g. to test with the same database type as production), add the
*external* Database URL to your local `.env` file as `DATABASE_URL=...` —
otherwise leave it unset locally and it'll keep using SQLite by default.

### Option B: PythonAnywhere (simple, good for students)
1. Sign up at https://www.pythonanywhere.com (free tier).
2. **Files** tab → upload/clone your GitHub repo via a Bash console:
   ```bash
   git clone https://github.com/your-username/online-voting-system.git
   ```
3. **Web** tab → **Add a new web app** → choose **Flask** → point it at your
   `app.py`.
4. Set up a virtualenv in the "Virtualenv" section and `pip install -r requirements.txt`.
5. Reload the web app. Your site is live at `yourusername.pythonanywhere.com`.

---

## Project structure

```
flask-voting-system/
├── app.py                  # all routes (home, voter, admin)
├── config.py                # app settings (secret key, DB path, mail, default admin)
├── extensions.py            # shared SQLAlchemy instance
├── mailer.py                  # Flask-Mail OTP sending (with on-screen fallback)
├── models.py                 # User, Admin, Candidate, ElectionConfig, Notification
├── utils.py                  # OTP generator + login-required decorators
├── requirements.txt
├── Procfile                  # for Render/Heroku-style deployment
├── .env.example               # copy to .env and fill in your mail credentials
├── static/css/style.css      # all styling
├── templates/                # Jinja HTML pages
│   ├── base.html
│   ├── home.html / login.html / signup.html / verify_otp.html
│   ├── dashboard.html / vote.html / thank_you.html
│   ├── results.html
│   └── admin_login.html / admin_dashboard.html / admin_users.html /
│       admin_candidates.html / admin_schedule.html
└── instance/voting.db        # SQLite DB (auto-created, gitignored)
```

## Security notes before using this for a real election
- Change `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` in `config.py`
  (or set the `ADMIN_USERNAME`/`ADMIN_PASSWORD` environment variables) before
  deploying anywhere public.
- Set a strong, random `SECRET_KEY` via environment variable in production.
- Wire up a real OTP delivery method (email/SMS) instead of the on-screen demo.
- Consider HTTPS-only cookies and rate-limiting login attempts for production use.
