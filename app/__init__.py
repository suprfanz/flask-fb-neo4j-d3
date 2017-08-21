from flask import Flask
from datetime import timedelta


# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# make the session timeout automatically after 2 hours
app.permanent_session_lifetime = timedelta(seconds=3599)

from app import views, models
