import os
from dotenv import load_dotenv
from together import Together

load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY")

PREPROMPT = """This response is supposed to be used as a tool for students in an 
            introductory Python course and should not directly generate answers 
            for students. Rather, the response should explain concepts and provide 
            code examples for students. The response is also generating a response
            for Discord so make sure that you are using markdowns correctly and that
            you are using hashtags for headers."""

print(f"Loaded API Key: {api_key}")

if not api_key:
    raise ValueError("No API key provided")

client = Together(api_key=api_key)

def generate_response(user_message: str) -> str:

    response = client.chat.completions.create(
        #AI model trained on Llama-3.3-70B-Instruct-Turbo
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[{"role": "system", "content": PREPROMPT}, {
                    "role": "user", "content": user_message}],
    )
    return response.choices[0].message.content.strip()