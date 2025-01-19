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
print("Connected to colonies with colonyname", colonyname)
executorid = "13803a04fcf4c8b8aba32988c62036dcfc854dd70c2aa5f8dd52905e744261ab"
executor_prvkey = "11bc9e79c99ff94c7ce75e1c582c20fffa232c02a6b203a2f9ae4802fc783c16"

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

def executor_loop():
    while (True):
        try:
            process = colonies.assign(colonyname, 10, executor_prvkey)
            print("Process", process.processid, "is assigned to HAL9000 executor")
            if process.spec.funcname == "alien":
                colonies.add_log(process.processid, "MonitorAgent: Alien lifeform detected!!" , executor_prvkey)

            func_spec = FuncSpec(
                funcname="chat",
                args=["Alien lifeform detected!!"],
                conditions = Conditions(
                    colonyname=colonyname,
                    executortype="hal9000",
                ),
                maxexectime=10,
                maxretries=0
            )

            colonies.submit_func_spec(func_spec, executor_prvkey)

            colonies.close(process.processid, [], executor_prvkey)
        except Exception as err:
            print(err)
            pass

if __name__ == "__main__":
    executor_loop() 
