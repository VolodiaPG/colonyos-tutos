import logging
import json
import argparse
import openai
import sys
import queue
from openai import OpenAI
import threading

# OpenAI config, API key be set with OPENAI_API_KEY environment variable
openai_config = {
    "model": "gpt-3.5-turbo",
    "base_url": "https://api.openai.com/v1/"
}

# Ollama config
ollama_config = {
    "model": "llama3.2",
    "base_url": "http://localhost:11434/v1/",
    "api_key": "ollama"
}

message_queue = queue.Queue()
done_queue = queue.Queue()
antenna_working = True

def check_status(args):
    print("System: Checking status of the spaceship!")
    if antenna_working:
        return "Checking status of the spaceship, all systems are operational, life support is at 100%, airlock is closed, antenna is working, we a week from Jupiter" 
    else:
        return "Checking status of the spaceship, all systems are operational, life support is at 100%, airlock is closed, antenna is NOT working"

def sound_alarm(args):
    print("System: Sounding the alarm!")
    return "Alarm has been sounded"

def fail_antenna(args):
    print("System: Failing the antenna!")
    global antenna_working
    antenna_working = False
    return "Antenna has been failed"

def define_rule(args):
    print("System: Defining rules...")
    rule = json.dumps(args["rules"])
    return "The following rule has been defined: " + rule + " Do not propose python code to the user, but rather show the rule in a human-readable format. Do not propose how to implement it"

assistant_functions = {
    "define_rule": define_rule,
    "check_status": check_status,
    "sound_alarm": sound_alarm,
    "fail_antenna": fail_antenna
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_status",
            "description": "Check the status of the spaceship."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sound_alarm",
            "description": "Sound the alarm. Only sound the alarm in case of an emergency."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fail_antenna",
            "description": "Fail the antenna."
        },
    },
    {
        "type": "function",
        "function": {
            "name": "define_rule",
            "description": (
                "Defines automation rules for home automation. "
                "Only use this function when the user explicitly asks to create, modify, or remove an automation rule."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "application_name": {
                        "type": "string",
                        "description": "The automation rule.",
                    },
                },
                "required": ["rules"],
                "additionalProperties": False,
            },
        },
    }
]

def chatbot_loop(model, client):
    messages = [
        {
            "role": "system",
            "content": (
                "You are HAL 9000" #, a polite AI home automation assistant. "
                "You should only call functions when explicitly requested by the user. "
                "Do NOT call any function unless the user explicitly asks you to perform an action."
                "Mission objective is to explore monolith orbiting Jupiter."
            )
        }
    ]

    while True:
        external_message = message_queue.get(block=True)
        messages.append({"role": "user", "content": external_message})

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools
            )
        except openai.NotFoundError as e:
            print(f'Error: {e}')
            continue
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            continue

        if not response.choices:
            print("No response received.")
            continue

        message = response.choices[0].message
        print(f'{message.content}')
        messages.append(message)

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")

                # if function_name == "define_rule" and "rules" not in external_message.lower():
                #     logging.warning(f"Skipping unintended function call: {function_name}")
                #     continue

                # print("--------------------------------------")
                # print(f"Tool call: {tool_call.function.name}")
                # print(f"Arguments: {tool_call.function.arguments}")
                # print("--------------------------------------")
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")

                logging.debug('Processing tool call: %s', function_name)

                func = assistant_functions.get(function_name)
                if func:
                    result = func(function_args)
                    result_message = {
                        "role": "tool",
                        "content": json.dumps({"result": str(result)}),
                        "tool_call_id": tool_call.id
                    }
                    messages.append(result_message)
        else:
            print(f'HAL9000: {response.choices[0].message.content}')
            continue

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            print(f'HAL9000: {response.choices[0].message.content}')
            messages.append(response.choices[0].message)

        except Exception as e:
            logging.error(f"Error processing follow-up response: {e}")
            done_queue.put(False)
        
        done_queue.put(True)

def user_input():
    print("Welcome to HAL9000! Type '/exit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "/exit":
            print("Exiting chatbot...")
            break
        if len(user_input) > 0:
            message_queue.put(user_input)
            done_queue.get(block=True)  # wait for the chatbot to finish processing
        else:
            print("Please enter a message.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LLM Chatbot')
    parser.add_argument('--api-key', type=str, default='', help='OpenAI API key')
    parser.add_argument('--base-url', type=str, default='', help='Base URL for the API')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--model', type=str, help='Language model selection')

    args = parser.parse_args()

    default_config = ollama_config

    if args.api_key:
        openai.api_key = args.api_key
    elif "api_key" in default_config:
        openai.api_key = default_config["api_key"]

    if args.base_url:
        openai.base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    elif "base_url" in default_config:
        openai.base_url = default_config["base_url"]

    if args.model:
        model = args.model
    else:
        model = default_config["model"]

    client = OpenAI(api_key=openai.api_key, base_url=openai.base_url)

    chatbot_thread = threading.Thread(target=chatbot_loop, args=(model, client), daemon=True)
    chatbot_thread.start()

    user_input()
