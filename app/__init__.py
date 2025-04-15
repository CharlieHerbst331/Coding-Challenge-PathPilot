# App initialization 
import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.config['SECRET_KEY'] = os.urandom(24)

# Import routes at the end to avoid circular imports
from app.routes import * 