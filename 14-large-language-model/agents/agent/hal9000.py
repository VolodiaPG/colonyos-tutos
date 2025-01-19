import logging
import json
import argparse
import openai
import queue
from openai import OpenAI
import threading
from pycolonies import FuncSpec, Conditions
from pycolonies import colonies_client

colonies, colonyname, colony_prvkey, _, _ = colonies_client()
executorid = "f682a0f034fcdeae797429bb779d8cdda425537acf045112f1bfd63f6d8eced8"
executor_prvkey = "ee7838c49280642f30b6b555e49641072a318d1979abac9f3e39aa4e59b029df"

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

def check_status(args):
    print("System: Checking status of the spaceship!")
    return "Checking status of the spaceship, all systems are operational, life support is at 100%"

def sound_alarm(args):
    print("System: Sounding the alarm!")

    func_spec = FuncSpec(
        funcname="setalarm",
        args=["true"],
        conditions = Conditions(
            colonyname=colonyname,
            executortype="spaceship",
        ),
        maxexectime=10,
        maxretries=0
    )
    
    process = colonies.submit_func_spec(func_spec, executor_prvkey)
    print("Process", process.processid, "submitted")

    return "Alarm has been sounded"

def detect_alien(args):
    print("System: Detecting alien life forms!")
    return "No alien life forms detected on onboard the ship."

def self_destruct(args):
    print("System: Self-destruct sequence initiated! The ship will self-destruct in T minus 20 seconds.")
    
    func_spec = FuncSpec(
        funcname="selfdestruct",
        args=["true"],
        conditions = Conditions(
            colonyname=colonyname,
            executortype="spaceship",
        ),
        maxexectime=10,
        maxretries=0
    )
    
    process = colonies.submit_func_spec(func_spec, executor_prvkey)
    print("Process", process.processid, "submitted")
    
    return "Self-destruct sequence initiated! The ship will self-destruct in T minus 20 seconds."

def define_rule(args):
    print("System: Defining rules...")
    rule = json.dumps(args["rules"])
    return "The following rule has been defined: " + rule + " Do not propose python code to the user, but rather show the rule in a human-readable format. Do not propose how to implement it"

assistant_functions = {
    "define_rule": define_rule,
    "check_status": check_status,
    "sound_alarm": sound_alarm,
    "detect_alien": detect_alien,
    "self_destruct": self_destruct
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
            "name": "detect_alien",
            "description": "Detect alien life forms onboard the ship."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "self_destruct",
            "description": "Self-destruct desruct the ship using a thermonuclear explosion equal to 200 Megatons."
        }
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
            reply = response.choices[0].message.content
            print(f'HAL9000: {reply}')
            done_queue.put(reply)
            continue

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            reply = response.choices[0].message.content
            print(f'HAL9000: {reply}')
            done_queue.put(reply)

        except Exception as e:
            logging.error(f"Error processing follow-up response: {e}")
            done_queue.put(False)

def user_input():
    print("Welcome to HAL9000! Type '/exit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "/exit":
            print("Exiting chatbot...")
            break
        if len(user_input) > 0:
            message_queue.put(user_input)
            # Wait for the chatbot to finish processing
            # Note this code is just for demonstration purposes, if the HAL9000 executor
            # is assigned a process, there will be a race condition between the chatbot
            # and the executor. This code is not production ready.
            done_queue.get(block=True)  
        else:
            print("Please enter a message.")

def executor_loop():
    while (True):
        try:
            process = colonies.assign(colonyname, 10, executor_prvkey)
            print("Process", process.processid, "is assigned to HAL9000 executor")
            if process.spec.funcname == "chat":
                message_queue.put(process.spec.args[0])
                result = done_queue.get(block=True)
                colonies.add_log(process.processid, "HAL9000" + result, executor_prvkey)

            colonies.close(process.processid, [], executor_prvkey)
        except Exception as err:
            print(err)
            pass

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
    
    executor_thread = threading.Thread(target=executor_loop, args=(), daemon=True)
    executor_thread.start()

    user_input()
