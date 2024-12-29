import os
import google.generativeai as genai
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_stock_analysis(stock_info, metrics):
    """Get AI-powered analysis of the stock"""
    try:
        logger.info(f"Generating AI analysis for {stock_info.get('symbol', 'Unknown Stock')}")

        prompt = f"""
        Analyze this stock based on the following metrics and provide investment insights.
        Format your response as a JSON string with exactly this structure:
        {{
            "summary": "Brief summary of the stock",
            "strengths": ["list", "of", "strengths"],
            "risks": ["list", "of", "risks"],
            "recommendation": "buy/hold/sell with brief explanation"
        }}

        Company: {stock_info.get('longName', '')}
        Sector: {stock_info.get('sector', '')}
        Current Price: ${stock_info.get('currentPrice', '')}
        P/E Ratio: {metrics.get('PE Ratio', '')}
        Market Cap: {metrics.get('Market Cap', '')}
        """

        if not GEMINI_API_KEY:
            logger.error("Gemini API key is not set")
            raise ValueError("Gemini API key is missing. Please set the GEMINI_API_KEY environment variable.")

        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')

        # Generate the response
        response = model.generate_content(prompt)

        # Parse the response text as JSON
        # The response text should be a JSON string
        analysis = json.loads(response.text)

        logger.info("Successfully generated AI analysis")
        return analysis

    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        return {
            "summary": "Unable to generate AI analysis: API key is missing.",
            "strengths": ["Please set up the Gemini API key to enable AI insights."],
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