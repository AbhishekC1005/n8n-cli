import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Configure the OpenAI client to point to NVIDIA's API endpoint
# Ensure you have NVIDIA_API_KEY set in your environment or .env file
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY")
)

# 1. Define your tool (a Python function)
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather in a given location."""
    return f"The weather in {location} is 22 degrees {unit}."

# 2. Define the tool schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

def main():
    print("Sending prompt to NVIDIA API...")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like in Paris today?"}
    ]

    # 3. Call the API using the NVIDIA base URL and your specified model
    # Note: Using the model name you provided. Ensure "kimi-k2" is a valid model name on the platform you are using,
    # or change it to an available NVIDIA NIM model like "meta/llama3-70b-instruct" if needed.
    model_name = "kimi-k2"
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024
        )

        response_message = response.choices[0].message
        tool_calls = getattr(response_message, "tool_calls", None)

        # 4. Check if the model decided to call a tool
        if tool_calls:
            print(f"\nThe model wants to call {len(tool_calls)} tool(s).")
            messages.append(response_message)
            
            # 5. Execute the tool call(s) locally
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Calling function: {function_name} with arguments: {function_args}")
                
                if function_name == "get_weather":
                    function_response = get_weather(
                        location=function_args.get("location"),
                        unit=function_args.get("unit", "celsius")
                    )
                    
                    print(f"Function result: {function_response}")
                    
                    # 6. Send the tool's result back to the model
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )

            print("\nSending tool results back to NVIDIA API for the final response...")
            # 7. Get the final response
            second_response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=1024
            )
            print("\nFinal Assistant Response:")
            print(second_response.choices[0].message.content)
            
        else:
            print("\nFinal Assistant Response (No tools called):")
            print(response_message.content)
            
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nNote: Make sure your NVIDIA_API_KEY is valid and that the model name is correct for the NVIDIA endpoint.")

if __name__ == "__main__":
    main()
