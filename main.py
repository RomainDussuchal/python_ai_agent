import os
from dotenv import load_dotenv
from google import genai
import sys

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents= sys.argv[1] ,
)
text = response.text
prompt_tokens = response.usage_metadata.prompt_token_count
response_tokens = response.usage_metadata.candidates_token_count
print(text)
print(f"Prompt tokens: {prompt_tokens}")
print(f"Response tokens: {response_tokens}")
