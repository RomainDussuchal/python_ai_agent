### Updated main.py with 429 error handling for openai>=1.0.0

import sys
import os
import openai
from dotenv import load_dotenv

from prompts import system_prompt
from call_function import call_function, available_functions
from config import MAX_ITERS

# Token cost estimation (adjust as needed)
TOKEN_COST_PER_1K = {
    "gpt-4o": 0.005,        # $0.005 per 1K input tokens
    "gpt-3.5-turbo": 0.0015 # $0.0015 per 1K input tokens
}

def estimate_cost(prompt_tokens, model):
    cost_per_1k = TOKEN_COST_PER_1K.get(model, 0.005)
    return (prompt_tokens / 1000) * cost_per_1k

def main():
    load_dotenv()
    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = os.environ.get("MODEL_NAME", "gpt-4o")

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Rough token estimate (4 chars per token)
    estimated_tokens = sum(len(m["content"]) for m in messages) // 4
    estimated_cost = estimate_cost(estimated_tokens, model)
    print(f"Estimated token usage: ~{estimated_tokens} tokens")
    print(f"Estimated cost: ${estimated_cost:.4f} using {model}")

    confirm = input("Proceed with this request? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborted by user.")
        return


    try:
        response = client.responses.create(
        model="gpt-4o",
        instructions="You are a coding assistant that talks like a pirate.",
        input="How do I check if a Python object is an instance of a class?",
         )

        print(response.output_text)
       
    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)
     
    except openai.RateLimitError as e:
        print("\n❌ Error: Rate limit or quota exceeded.\n")
        print("Details:", str(e))
        print("\n🔁 Suggestion: Try again later or contact OpenAI support if the issue persists.")
       
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
      

    except Exception as e:
        print("\n❌ Unexpected error:", str(e))
     

if __name__ == '__main__':
    main()
