import logging
from datetime import datetime
from .ai_advisor import get_stock_analysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialGoal:
    def __init__(self, goal_type, target_amount, target_date, current_amount=0):
        self.goal_type = goal_type
        self.target_amount = float(target_amount)
        self.target_date = datetime.strptime(target_date, "%Y-%m-%d")
        self.current_amount = float(current_amount)
        self.progress = (self.current_amount / self.target_amount) * 100 if target_amount > 0 else 0

def analyze_goal_feasibility(goal, income, expenses):
    """Analyze the feasibility of a financial goal"""
    try:
        months_remaining = (goal.target_date - datetime.now()).days / 30
        amount_needed = goal.target_amount - goal.current_amount
        
        monthly_savings = income - expenses
        projected_savings = monthly_savings * months_remaining
        
        feasibility = {
            "goal_type": goal.goal_type,
            "target_amount": goal.target_amount,
            "current_progress": goal.progress,
            "monthly_required": amount_needed / months_remaining if months_remaining > 0 else 0,
            "projected_savings": projected_savings,
            "is_achievable": projected_savings >= amount_needed,
            "recommendation": ""
        }
        
        # Generate recommendation based on feasibility
        if projected_savings >= amount_needed:
            feasibility["recommendation"] = (
                f"Goal appears achievable with current savings rate. "
                f"Continue saving ${monthly_savings:.2f} monthly."
            )
        else:
            additional_needed = (amount_needed - projected_savings) / months_remaining
            feasibility["recommendation"] = (
                f"Goal may be challenging. Consider increasing monthly savings "
                f"by ${additional_needed:.2f} or adjusting the target date."
            )
        
        return feasibility
    except Exception as e:
        logger.error(f"Error analyzing goal feasibility: {str(e)}")
        raise Exception(f"Failed to analyze goal feasibility: {str(e)}")

def generate_investment_plan(goal, risk_tolerance):
    """Generate an investment plan to meet financial goals"""
    try:
        # Calculate time horizon in years
        years_to_goal = (goal.target_date - datetime.now()).days / 365
        
        # Adjust investment strategy based on time horizon and risk tolerance
        if years_to_goal < 2:
            strategy = "conservative"
        elif years_to_goal < 5:
            strategy = "moderate"
        else:
            strategy = "aggressive"
            
        # Override with user's risk tolerance if more conservative
        if risk_tolerance == "conservative" and strategy != "conservative":
            strategy = "moderate"
            
        investment_strategies = {
            "conservative": {
                "stocks": 30,
                "bonds": 60,
                "cash": 10
            },
            "moderate": {
                "stocks": 60,
                "bonds": 35,
                "cash": 5
            },
            "aggressive": {
                "stocks": 80,
                "bonds": 15,
                "cash": 5
            }
        }
        
        selected_strategy = investment_strategies[strategy]
        
        return {
            "goal_type": goal.goal_type,
            "time_horizon": years_to_goal,
            "strategy": strategy,
            "allocation": selected_strategy,
            "monthly_investment_needed": (
                (goal.target_amount - goal.current_amount) / 
                (years_to_goal * 12) if years_to_goal > 0 else 0
            )
        }
    except Exception as e:
        logger.error(f"Error generating investment plan: {str(e)}")
        raise Exception(f"Failed to generate investment plan: {str(e)}")

def track_goal_progress(goal, transactions):
    """Track progress towards a financial goal"""
    try:
        # Calculate current progress
        current_progress = {
            "goal_type": goal.goal_type,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "progress_percentage": goal.progress,
            "remaining_amount": goal.target_amount - goal.current_amount,
            "last_update": datetime.now().isoformat(),
            "recent_transactions": transactions[-5:] if transactions else []
        }
        
        return current_progress
    except Exception as e:
        logger.error(f"Error tracking goal progress: {str(e)}")
        raise Exception(f"Failed to track goal progress: {str(e)}")
