import os
from openai import OpenAI
import json

# Ensure you have your OPENAI_API_KEY set in your environment variables,
# or in a .env file if using python-dotenv.
client = OpenAI()

# 1. Define your tool (a Python function)
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather in a given location."""
    # In a real app, you would call a weather API here.
    # We will return dummy data for demonstration.
    return f"The weather in {location} is 22 degrees {unit}."

# 2. Define the tool schema for OpenAI
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
    print("Sending prompt to OpenAI...")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like in Paris today?"}
    ]

    # 3. Call the API and pass the tools definition
    response = client.chat.completions.create(
        model="gpt-4o", # or gpt-3.5-turbo
        messages=messages,
        tools=tools,
        tool_choice="auto" 
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 4. Check if the model decided to call a tool
    if tool_calls:
        print(f"\nThe model wants to call {len(tool_calls)} tool(s).")
        messages.append(response_message) # Append the model's response to the conversation history
        
        # 5. Execute the tool call(s) locally
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"Calling function: {function_name} with arguments: {function_args}")
            
            if function_name == "get_weather":
                # Call the actual Python function
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

        print("\nSending tool results back to OpenAI to get the final response...")
        # 7. Get the final response from the model
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        print("\nFinal Assistant Response:")
        print(second_response.choices[0].message.content)
    else:
        print("\nFinal Assistant Response:")
        print(response_message.content)

if __name__ == "__main__":
    main()
