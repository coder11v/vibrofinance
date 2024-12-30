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
        self.SUPERUSER = "theyounginvestor"

    def _ensure_db_exists(self):
        """Ensure the database directory and file exist"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            if not os.path.exists(self.db_path):
                with open(self.db_path, 'w') as f:
                    json.dump({"users": {}, "chat_messages": [], "notifications": {}}, f)
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

    def is_superuser(self, username: str) -> bool:
        """Check if user is a superuser"""
        return username == self.SUPERUSER

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

            message_id = len(db["chat_messages"])  # Simple incrementing ID
            db["chat_messages"].append({
                "id": message_id,
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

    def delete_message(self, message_id: int, username: str) -> bool:
        """Delete a chat message (superuser only)"""
        try:
            if not self.is_superuser(username):
                return False

            db = self._load_db()
            db["chat_messages"] = [msg for msg in db["chat_messages"] if msg.get("id") != message_id]
            self._save_db(db)
            return True
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
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

    def get_all_users(self, username: str) -> Optional[List[Dict]]:
        """Get list of all users (superuser only)"""
        try:
            if not self.is_superuser(username):
                return None

            db = self._load_db()
            users_list = []
            for username, data in db["users"].items():
                users_list.append({
                    "username": username,
                    "created_at": data["created_at"],
                    "last_login": data["last_login"],
                    "is_superuser": self.is_superuser(username)
                })
            return users_list
        except Exception as e:
            logger.error(f"Error getting users list: {str(e)}")
            return None

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

    def send_notification(self, from_username: str, to_username: str, message: str) -> bool:
        """Send a notification to a user (superuser only)"""
        try:
            if not self.is_superuser(from_username):
                return False

            db = self._load_db()
            if "notifications" not in db:
                db["notifications"] = {}

            if to_username not in db["notifications"]:
                db["notifications"][to_username] = []

            notification = {
                "id": len(db["notifications"][to_username]),
                "from": from_username,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }

            db["notifications"][to_username].append(notification)
            self._save_db(db)
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False

    def get_notifications(self, username: str) -> List[Dict]:
        """Get notifications for a user"""
        try:
            db = self._load_db()
            return db.get("notifications", {}).get(username, [])
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return []

    def mark_notification_as_read(self, username: str, notification_id: int) -> bool:
        """Mark a notification as read"""
        try:
            db = self._load_db()
            notifications = db.get("notifications", {}).get(username, [])

            for notification in notifications:
                if notification["id"] == notification_id:
                    notification["read"] = True
                    break

            self._save_db(db)
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False

    def send_notification_to_all(self, from_username: str, message: str) -> bool:
        """Send a notification to all users (superuser only)"""
        try:
            if not self.is_superuser(from_username):
                return False

            db = self._load_db()
            users = list(db["users"].keys())
            success = True

            for username in users:
                if username != from_username:  # Don't send to self
                    if "notifications" not in db:
                        db["notifications"] = {}
                    if username not in db["notifications"]:
                        db["notifications"][username] = []

                    notification = {
                        "id": len(db["notifications"][username]),
                        "from": from_username,
                        "message": message,
                        "timestamp": datetime.now().isoformat(),
                        "read": False
                    }
                    db["notifications"][username].append(notification)

            self._save_db(db)
            return success
        except Exception as e:
            logger.error(f"Error sending notification to all users: {str(e)}")
            return False