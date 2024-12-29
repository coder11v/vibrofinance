import logging
import pandas as pd
from datetime import datetime
from .stock_data import get_multiple_stocks_data, calculate_technical_indicators
from .ai_advisor import get_stock_analysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_portfolio_recommendation(risk_tolerance, investment_amount, preferences=None):
    """Generate AI-powered portfolio recommendations"""
    try:
        # Default sectors for diversification
        sectors = [
            "Technology", "Healthcare", "Financial Services",
            "Consumer Cyclical", "Industrial"
        ]
        
        # Map risk tolerance to portfolio composition
        allocations = {
            "conservative": {"stocks": 0.40, "bonds": 0.60},
            "moderate": {"stocks": 0.60, "bonds": 0.40},
            "aggressive": {"stocks": 0.80, "bonds": 0.20}
        }
        
        # Get allocation based on risk tolerance
        allocation = allocations.get(risk_tolerance.lower(), allocations["moderate"])
        
        return {
            "allocation": allocation,
            "investment_amount": investment_amount,
            "recommended_sectors": sectors,
            "risk_profile": risk_tolerance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating portfolio recommendation: {str(e)}")
        raise Exception(f"Failed to generate portfolio recommendation: {str(e)}")

def analyze_portfolio_health(portfolio_stocks):
    """Analyze the health and balance of a portfolio"""
    try:
        # Get current data for all stocks in portfolio
        stock_data = get_multiple_stocks_data(portfolio_stocks)
        
        # Calculate portfolio metrics
        portfolio_metrics = {
            "total_value": 0,
            "sector_allocation": {},
            "risk_metrics": {},
            "recommendations": []
        }
        
        # Analyze each stock
        for symbol, data in stock_data.items():
            # Get AI analysis for each stock
            analysis = get_stock_analysis(data['info'], 
                                       {"Market Cap": data['info'].get('marketCap'),
                                        "PE Ratio": data['info'].get('trailingPE')})
            
            portfolio_metrics["recommendations"].append({
                "symbol": symbol,
                "analysis": analysis
            })
            
            # Add sector data
            sector = data['info'].get('sector', 'Unknown')
            if sector in portfolio_metrics["sector_allocation"]:
                portfolio_metrics["sector_allocation"][sector] += 1
            else:
                portfolio_metrics["sector_allocation"][sector] = 1
        
        return portfolio_metrics
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        raise Exception(f"Failed to analyze portfolio: {str(e)}")

def calculate_rebalancing_needs(current_allocation, target_allocation):
    """Calculate portfolio rebalancing requirements"""
    try:
        differences = {}
        for asset, current_pct in current_allocation.items():
            target_pct = target_allocation.get(asset, 0)
            diff = target_pct - current_pct
            differences[asset] = {
                "current": current_pct,
                "target": target_pct,
                "difference": diff,
                "action": "buy" if diff > 0 else "sell",
                "magnitude": abs(diff)
            }
        return differences
    except Exception as e:
        logger.error(f"Error calculating rebalancing needs: {str(e)}")
        raise Exception(f"Failed to calculate rebalancing needs: {str(e)}")
