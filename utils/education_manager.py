import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EducationManager:
    def __init__(self, data_path: str = "data/courses.json"):
        self.data_path = data_path
        self._ensure_data_exists()

    def _ensure_data_exists(self):
        """Ensure the courses data file exists"""
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            if not os.path.exists(self.data_path):
                initial_data = {
                    "courses": [
                        {
                            "id": "investing-101",
                            "title": "Investing 101",
                            "description": "Learn the basics of investing and financial markets",
                            "difficulty": "Beginner",
                            "duration": "2 hours",
                            "modules": [
                                {
                                    "id": "module-1",
                                    "title": "Understanding Stocks",
                                    "content": "Learn what stocks are and how they work...",
                                    "quiz": [
                                        {
                                            "question": "What is a stock?",
                                            "options": [
                                                "A type of bond",
                                                "Ownership in a company",
                                                "A savings account",
                                                "A type of mutual fund"
                                            ],
                                            "correct": 1
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "user_progress": {}
                }
                with open(self.data_path, 'w') as f:
                    json.dump(initial_data, f, indent=4)
        except Exception as e:
            logger.error(f"Error ensuring data exists: {str(e)}")
            raise

    def _load_data(self) -> Dict:
        """Load the courses data"""
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _save_data(self, data: Dict):
        """Save the courses data"""
        try:
            with open(self.data_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            raise

    def get_all_courses(self) -> List[Dict]:
        """Get all available courses"""
        try:
            data = self._load_data()
            return data["courses"]
        except Exception as e:
            logger.error(f"Error getting courses: {str(e)}")
            return []

    def get_course(self, course_id: str) -> Optional[Dict]:
        """Get a specific course by ID"""
        try:
            data = self._load_data()
            for course in data["courses"]:
                if course["id"] == course_id:
                    return course
            return None
        except Exception as e:
            logger.error(f"Error getting course: {str(e)}")
            return None

    def get_user_progress(self, username: str) -> Dict:
        """Get user's course progress"""
        try:
            data = self._load_data()
            return data["user_progress"].get(username, {})
        except Exception as e:
            logger.error(f"Error getting user progress: {str(e)}")
            return {}

    def update_user_progress(self, username: str, course_id: str, module_id: str, completed: bool = True) -> bool:
        """Update user's progress in a course module"""
        try:
            data = self._load_data()
            
            if username not in data["user_progress"]:
                data["user_progress"][username] = {}
            
            if course_id not in data["user_progress"][username]:
                data["user_progress"][username][course_id] = {
                    "modules": {},
                    "started_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            
            data["user_progress"][username][course_id]["modules"][module_id] = {
                "completed": completed,
                "completed_at": datetime.now().isoformat() if completed else None
            }
            data["user_progress"][username][course_id]["last_updated"] = datetime.now().isoformat()
            
            self._save_data(data)
            return True
        except Exception as e:
            logger.error(f"Error updating user progress: {str(e)}")
            return False

    def get_module_completion(self, username: str, course_id: str, module_id: str) -> bool:
        """Check if a user has completed a specific module"""
        try:
            progress = self.get_user_progress(username)
            return progress.get(course_id, {}).get("modules", {}).get(module_id, {}).get("completed", False)
        except Exception as e:
            logger.error(f"Error checking module completion: {str(e)}")
            return False
