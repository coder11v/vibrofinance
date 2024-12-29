import os
from openai import OpenAI
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_stock_analysis(stock_info, metrics):
    """Get AI-powered analysis of the stock"""
    try:
        logger.info(f"Generating AI analysis for {stock_info.get('symbol', 'Unknown Stock')}")

        prompt = f"""
        Analyze this stock based on the following metrics and provide investment insights:

        Company: {stock_info.get('longName', '')}
        Sector: {stock_info.get('sector', '')}
        Current Price: ${stock_info.get('currentPrice', '')}
        P/E Ratio: {metrics.get('PE Ratio', '')}
        Market Cap: {metrics.get('Market Cap', '')}

        Provide analysis in JSON format with the following structure:
        {{
            "summary": "Brief summary of the stock",
            "strengths": ["list", "of", "strengths"],
            "risks": ["list", "of", "risks"],
            "recommendation": "buy/hold/sell with brief explanation"
        }}
        """

        if not OPENAI_API_KEY:
            logger.error("OpenAI API key is not set")
            raise ValueError("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional financial analyst providing stock market insights."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        analysis = json.loads(response.choices[0].message.content)
        logger.info("Successfully generated AI analysis")
        return analysis

    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        return {
            "summary": "Unable to generate AI analysis: API key is missing.",
            "strengths": ["Please set up the OpenAI API key to enable AI insights."],
            "risks": ["Contact administrator to configure the API key."],
            "recommendation": "API configuration required."
        }
    except Exception as e:
        logger.error(f"Error generating AI analysis: {str(e)}")
        return {
            "summary": "Unable to generate AI analysis at this time.",
            "strengths": ["Data available but analysis is temporarily unavailable."],
            "risks": ["Try refreshing the page or try again later."],
            "recommendation": "Please try again in a few moments."
        }