from flask_sqlalchemy import SQLAlchemy

# A single shared db object, imported by both app.py and models.py.
# This avoids circular-import problems.
db = SQLAlchemy()
