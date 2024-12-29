import os
import google.generativeai as genai
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def clean_json_string(text):
    """Clean the response text to extract valid JSON"""
    try:
        # Find the first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return text[start:end]
        return text
    except Exception as e:
        logger.error(f"Error cleaning JSON string: {str(e)}")
        return text

def validate_analysis(analysis):
    """Validate that the analysis contains all required fields"""
    required_fields = ['summary', 'strengths', 'risks', 'recommendation']
    for field in required_fields:
        if field not in analysis:
            raise ValueError(f"Missing required field: {field}")
        if field in ['strengths', 'risks'] and not isinstance(analysis[field], list):
            analysis[field] = [analysis[field]]  # Convert to list if it's a single string

def get_stock_analysis(stock_info, metrics):
    """Get AI-powered analysis of the stock"""
    try:
        logger.info(f"Generating AI analysis for {stock_info.get('symbol', 'Unknown Stock')}")

        prompt = f"""
        You are a professional financial analyst. Analyze this stock and provide investment insights.

        Stock Information:
        - Company: {stock_info.get('longName', 'Unknown')}
        - Sector: {stock_info.get('sector', 'Unknown')}
        - Current Price: ${stock_info.get('currentPrice', 'N/A')}
        - P/E Ratio: {metrics.get('PE Ratio', 'N/A')}
        - Market Cap: {metrics.get('Market Cap', 'N/A')}
        - EPS: {metrics.get('EPS', 'N/A')}
        - Dividend Yield: {metrics.get('Dividend Yield', 'N/A')}

        Provide your analysis in the following JSON format EXACTLY (no markdown, no additional text):
        {{
            "summary": "A concise summary of the stock's current position and outlook",
            "strengths": ["strength1", "strength2", "strength3"],
            "risks": ["risk1", "risk2", "risk3"],
            "recommendation": "A clear buy/hold/sell recommendation with brief explanation"
        }}
        """

        if not GEMINI_API_KEY:
            logger.error("Gemini API key is not set")
            raise ValueError("Gemini API key is missing. Please set the GEMINI_API_KEY environment variable.")

        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')

        # Generate the response
        response = model.generate_content(prompt)

        # Clean and parse the response
        cleaned_response = clean_json_string(response.text)
        analysis = json.loads(cleaned_response)

        # Validate the analysis structure
        validate_analysis(analysis)

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
    except json.JSONDecodeError as je:
        logger.error(f"JSON parsing error: {str(je)}")
        return {
            "summary": "Unable to process AI analysis response.",
            "strengths": ["Data is available but couldn't be processed."],
            "risks": ["Try refreshing or analyzing a different stock."],
            "recommendation": "Please try again with a different stock or time period."
        }
    except Exception as e:
        logger.error(f"Error generating AI analysis: {str(e)}")
        return {
            "summary": "Unable to generate AI analysis at this time.",
            "strengths": ["Technical issue encountered while generating analysis."],
            "risks": ["Temporary API or processing error."],
            "recommendation": "Please try again in a few moments."
        }