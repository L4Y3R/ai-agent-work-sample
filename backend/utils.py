import logging
import re
from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI()

def verify_query(text: str) -> bool:
    """Basic rule-based gibberish detector"""
    if len(text.strip()) < 4:
        return True
    if re.fullmatch(r"[a-zA-Z]{6,}", text) and not any(word in text.lower() for word in ["temp", "humid", "co2", "air", "room", "sensor", "data"]):
        return True
    return False

def is_query_valid(query: str) -> bool:
    """Use GPT to classify if the query is meaningful for air quality"""
    if verify_query(query):
        return False

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a validator. Only respond with 'Yes' or 'No'. "
                        "Is the user query meaningful and related to air quality analysis? "
                        "Examples: temperature trends, humidity, CO2 levels, air quality per room."
                    ),
                },
                {"role": "user", "content": f"Query: {query}"},
            ],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer.startswith("yes")
    except Exception as e:
        logger.error(f"Query classification failed: {e}")
        return False
