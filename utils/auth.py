import json
import hashlib
import os
from datetime import datetime
import logging
from typing import Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, db_path: str = "data/users.json"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the database directory and file exist"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            if not os.path.exists(self.db_path):
                with open(self.db_path, 'w') as f:
                    json.dump({"users": {}, "chat_messages": []}, f)
        except Exception as e:
            logger.error(f"Error ensuring database exists: {str(e)}")
            raise

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _load_db(self) -> Dict:
        """Load the JSON database"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {str(e)}")
            raise

    def _save_db(self, data: Dict):
        """Save data to the JSON database"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving database: {str(e)}")
            raise

    def register_user(self, username: str, password: str) -> bool:
        """Register a new user"""
        try:
            db = self._load_db()
            if username in db["users"]:
                return False

            db["users"][username] = {
                "password": self._hash_password(password),
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "search_history": [],
                "portfolio": [],
                "goals": []
            }
            self._save_db(db)
            return True
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False

    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        try:
            db = self._load_db()
            user = db["users"].get(username)
            if user and user["password"] == self._hash_password(password):
                # Update last login
                db["users"][username]["last_login"] = datetime.now().isoformat()
                self._save_db(db)
                return True
            return False
        except Exception as e:
            logger.error(f"Error verifying user: {str(e)}")
            return False

    def save_chat_message(self, username: str, message: str) -> bool:
        """Save a chat message"""
        try:
            db = self._load_db()
            if "chat_messages" not in db:
                db["chat_messages"] = []

            db["chat_messages"].append({
                "username": username,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })

            # Keep only last 100 messages
            if len(db["chat_messages"]) > 100:
                db["chat_messages"] = db["chat_messages"][-100:]

            self._save_db(db)
            return True
        except Exception as e:
            logger.error(f"Error saving chat message: {str(e)}")
            return False

    def get_chat_messages(self, limit: int = 50) -> List[Dict]:
        """Get recent chat messages"""
        try:
            db = self._load_db()
            messages = db.get("chat_messages", [])
            return messages[-limit:] if messages else []
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            return []

    def save_user_activity(self, username: str, activity_type: str, data: Dict):
        """Save user activity (searches, analyses, etc.)"""
        try:
            db = self._load_db()
            if username in db["users"]:
                if activity_type == "search":
                    db["users"][username]["search_history"].append({
                        "timestamp": datetime.now().isoformat(),
                        "symbol": data.get("symbol"),
                        "period": data.get("period")
                    })
                elif activity_type == "portfolio":
                    db["users"][username]["portfolio"] = data
                elif activity_type == "goals":
                    db["users"][username]["goals"] = data

                self._save_db(db)
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving user activity: {str(e)}")
            return False

    def get_user_data(self, username: str) -> Optional[Dict]:
        """Get user data including history"""
        try:
            db = self._load_db()
            return db["users"].get(username)
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None

    def get_search_history(self, username: str) -> List[Dict]:
        """Get user's search history"""
        try:
            db = self._load_db()
            user = db["users"].get(username)
            return user.get("search_history", []) if user else []
        except Exception as e:
            logger.error(f"Error getting search history: {str(e)}")
            return []