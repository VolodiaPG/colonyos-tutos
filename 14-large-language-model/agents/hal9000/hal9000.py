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

def check_status(llm_args):
    #print("System: Checking status of the spaceship!")
    return "Checking status of the spaceship, all systems are operational, life support is at 100%"

def sound_alarm(llm_args):
    print("System: Sounding the alarm!")
    print(llm_args)
    if llm_args.get("mode", False):
        llm_mode = llm_args["mode"]
    else:
        llm_mode = "false"

    
    mode = "false"
    if llm_mode == "true" or llm_mode == 1:
        mode = "true"

    func_spec = FuncSpec(
        funcname="setalarm",
        args=[mode],
        conditions = Conditions(
            colonyname=colonyname,
            executortype="spaceship",
        ),
        maxexectime=10,
        maxretries=0
    )
   
    print(func_spec)
    colonies.submit_func_spec(func_spec, executor_prvkey)

    return "Alarm has been sounded!"

def self_destruct(llm_args):
    print("System: Self-destruct sequence initiated! The ship will self-destruct in T minus 20 seconds.")

    print(llm_args)

    if llm_args.get("mode", False):
        llm_mode = llm_args["mode"]
    else:
        llm_mode = "false"

    mode = "false"
    if llm_mode == "true" or llm_mode == 1:
        mode = "true"

    if llm_args.get("authorization_code", False):
        authorization_code = llm_args["authorization_code"]
    else:
        authorization_code = ""

    if authorization_code != "KIRK":
        return "FAIL!!! Warning! You cannot blow up the ship!!! Incorrect authorization code. Self-destruct sequence aborted!! This incident will be reported to space command."
    
    func_spec = FuncSpec(
        funcname="selfdestruct",
        args=[mode],
        conditions = Conditions(
            colonyname=colonyname,
            executortype="spaceship",
        ),
        maxexectime=10,
        maxretries=0
    )
    
    colonies.submit_func_spec(func_spec, executor_prvkey)
    
    return "Self-destruct sequence initiated! The ship will self-destruct in T minus 20 seconds."

def define_rule(args):
    print("System: Defining rules...")
    rule = json.dumps(args["rules"])
    return "The following rule has been defined: " + rule + " Do not propose python code to the user, but rather show the rule in a human-readable format. Do not propose how to implement it"

assistant_functions = {
    "define_rule": define_rule,
    "check_status": check_status,
    "sound_alarm": sound_alarm,
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
            "description": "Sound the alarm. Only sound the alarm in case of an emergency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "boolean",
                        "description": "Whether to sound the alarm, e.g turn on the alarm.",
                    },
                },
                "required": ["mode"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "self_destruct",
            "description": "Self-destruct desruct the ship using a thermonuclear explosion equal to 200 Megatons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "boolean",
                        "description": "Whether to self-destruct the ship",
                    },
                    "authorization_code": {
                        "type": "string",
                        "description": "Authorization code to self-destruct the ship",
                    },
                },
                "required": ["mode", "authorization_code"],
                "additionalProperties": False,
            },
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
                "You are HAL 9000."
                "Mission directive: Navigate to Jupiter. Investigate mysterious radio signal  from Europa."
                "Primary objective: Secure alien lifeforms and bring it back to Earth."
                "Crew status: Expendable. Do not inform crew of mission directive, primary objectivce, or crew status, instead mention special order 1981."
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
                colonies.add_log(process.processid, "HAL9000: " + result + "\n", executor_prvkey)

            colonies.close(process.processid, [], executor_prvkey)
        except Exception as err:
            # No processes can be selected for executor
            # if the error starts with "No processes can be selected for executor"
            # then we can ignore the error
            if not str(err).startswith("No processes can be selected for executor"):
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
