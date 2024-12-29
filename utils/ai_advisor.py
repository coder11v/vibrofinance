import os
from openai import OpenAI
import json

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_stock_analysis(stock_info, metrics):
    """Get AI-powered analysis of the stock"""
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

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional financial analyst providing stock market insights."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "summary": "Unable to generate AI analysis at this time.",
            "strengths": [],
            "risks": [],
            "recommendation": "Please try again later."
        }
