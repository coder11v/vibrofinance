import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database files
DB_FOLDER = "db"
USERS_FILE = os.path.join(DB_FOLDER, "users.json")
CHATS_FILE = os.path.join(DB_FOLDER, "chats.json")
INSIGHTS_FILE = os.path.join(DB_FOLDER, "insights.json")

# Create db folder if it doesn't exist
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

def load_json(file_path):
    """Load JSON data from file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        return {}

def save_json(file_path, data):
    """Save JSON data to file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {str(e)}")
        raise

class JSONDatabase:
    def __init__(self):
        self.users = load_json(USERS_FILE)
        self.chats = load_json(CHATS_FILE)
        self.insights = load_json(INSIGHTS_FILE)

    def save(self):
        """Save all data to files"""
        save_json(USERS_FILE, self.users)
        save_json(CHATS_FILE, self.chats)
        save_json(INSIGHTS_FILE, self.insights)

# Database instance
db = JSONDatabase()

def get_db():
    return db