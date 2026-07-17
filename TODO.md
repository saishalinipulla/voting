# TODO - Fix bugs (OTP email), performance, and production readiness

- [x] Step 1: Fix OTP email delivery issues
  - [x] app.py: remove MAIL_USERNAME/MAIL_PASSWORD debug prints
  - [x] app.py: improve /signup behavior when email fails (clear flash + session flags)
  - [x] mailer.py: remove duplicate dead `except` block; add config validation/logging
  - [x] config.py: add missing Flask-Mail settings defaults (MAIL_USE_SSL, MAIL_DEFAULT_SENDER fallback)


- [ ] Step 2: Improve app loading speed
  - [ ] Ensure gunicorn is used in Dockerfile (replace python app.py)
  - [ ] Optionally adjust gunicorn args in render.yaml/Procfile

- [ ] Step 3: Bug hygiene / stability
  - [ ] Remove unnecessary overhead/debug settings
  - [ ] Smoke test key flows (signup→verify, resend, login, admin pages)

- [ ] Step 4: Git workflow
  - [ ] git status / branch / pull latest
  - [ ] create branch `blackboxai/<name>`
  - [ ] commit changes
  - [ ] push to GitHub

