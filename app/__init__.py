from flask import Flask

app = Flask(__name__)

# Create SQLite3 database with Flask-SQLAlchemy
app.config.from_object("config")

from . import views
from . import forms
from . import models