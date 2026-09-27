import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def ask_gemini(prompt):

    models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite"
    ]

    last_error = None

    for model in models:

        for attempt in range(2):

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                return response.text

            except Exception as error:
                last_error = error
                time.sleep(2)

    raise last_error