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
                            "id": "vib-investing-101",
                            "title": "VIB Investing 101",
                            "description": "Master the fundamentals of investing with VIB's comprehensive beginner course. Learn market basics, risk management, and smart investment strategies.",
                            "difficulty": "Beginner",
                            "duration": "4 hours",
                            "url": "invest.veerbajaj.com",
                            "modules": [
                                {
                                    "id": "module-1",
                                    "title": "Understanding Stock Markets",
                                    "content": """
# Introduction to Stock Markets

The stock market is a vital component of the global economy where shares of publicly traded companies are bought and sold. Here's what you need to know:

## Key Concepts
- Stocks represent ownership in a company
- Markets operate on supply and demand
- Prices reflect company value and market sentiment

## Why Invest in Stocks?
1. Potential for long-term growth
2. Dividend income
3. Portfolio diversification
4. Hedge against inflation
                                    """,
                                    "quiz": [
                                        {
                                            "question": "What does owning a stock represent?",
                                            "options": [
                                                "A loan to a company",
                                                "Ownership in a company",
                                                "A promise to buy products",
                                                "A job guarantee"
                                            ],
                                            "correct": 1
                                        }
                                    ]
                                },
                                {
                                    "id": "module-2",
                                    "title": "Investment Strategies",
                                    "content": """
# Investment Strategies

Learn about different approaches to investing and how to choose the right strategy for your goals.

## Common Strategies
1. Value Investing
2. Growth Investing
3. Dividend Investing
4. Index Investing

## Risk Management
- Diversification
- Asset Allocation
- Position Sizing
                                    """,
                                    "quiz": [
                                        {
                                            "question": "What is diversification?",
                                            "options": [
                                                "Buying only tech stocks",
                                                "Investing in different asset classes to reduce risk",
                                                "Selling all investments at once",
                                                "Borrowing money to invest"
                                            ],
                                            "correct": 1
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "technical-analysis",
                            "title": "Technical Analysis Masterclass",
                            "description": "Learn how to analyze stock charts, identify patterns, and make data-driven investment decisions.",
                            "difficulty": "Intermediate",
                            "duration": "6 hours",
                            "modules": [
                                {
                                    "id": "module-1",
                                    "title": "Chart Patterns & Indicators",
                                    "content": """
# Technical Analysis Fundamentals

Learn to read and interpret stock charts using technical indicators.

## Key Topics
- Support and Resistance
- Moving Averages
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
                                    """,
                                    "quiz": [
                                        {
                                            "question": "What does RSI measure?",
                                            "options": [
                                                "Stock price",
                                                "Trading volume",
                                                "Price momentum and overbought/oversold conditions",
                                                "Company earnings"
                                            ],
                                            "correct": 2
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "risk-management",
                            "title": "Risk Management Essentials",
                            "description": "Master the art of protecting your investments through effective risk management strategies.",
                            "difficulty": "Advanced",
                            "duration": "3 hours",
                            "modules": [
                                {
                                    "id": "module-1",
                                    "title": "Understanding Risk Types",
                                    "content": """
# Types of Investment Risk

Learn about different risks in investing and how to manage them effectively.

## Risk Categories
1. Market Risk
2. Credit Risk
3. Liquidity Risk
4. Operational Risk

## Risk Mitigation Strategies
- Stop Loss Orders
- Position Sizing
- Portfolio Rebalancing
                                    """,
                                    "quiz": [
                                        {
                                            "question": "What is a stop-loss order?",
                                            "options": [
                                                "An order to buy more stocks",
                                                "An order to automatically sell if price falls below a certain level",
                                                "A guarantee against losses",
                                                "A type of dividend payment"
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