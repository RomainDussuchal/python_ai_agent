import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from prompts import system_prompt
from call_function import call_function, available_functions
from config import MAX_ITERS


def main():
    load_dotenv()
    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
   

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    iters = 0
    while True:
        iters += 1
        if iters > MAX_ITERS:
            print(f"Maximum iterations ({MAX_ITERS}) reached.")
            sys.exit(1)

        try:
            result = generate_content(client, messages, verbose)
            if result:
                print(result)
                break

            user_input = input("\nYou: ")
            messages.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
        except Exception as e:
            print(f"Error in generate_content: {e}")



def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    if response.function_calls:
        function_responses = []
        for function_call_part in response.function_calls:
            function_result = call_function(function_call_part, verbose)
            if (
                not function_result.parts
                or not function_result.parts[0].function_response
            ):
                raise Exception("empty function call result")
            if verbose:
                print(f"-> {function_result.parts[0].function_response.response}")
            function_responses.append(function_result.parts[0])

        # Add tool responses to messages and return to loop
        messages.append(types.Content(role="tool", parts=function_responses))
        return None

    # If no function call, just respond as assistant and keep loop going
    if response.text:
        messages.append(types.Content(role="assistant", parts=[types.Part(text=response.text)]))
        print(response.text)

    return None

if __name__ == "__main__":
    main()
