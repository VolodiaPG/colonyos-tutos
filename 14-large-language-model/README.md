# Getting start
ColonyOS is fundamentally designed around the concept of function invocation. When a function is called, it is wrapped into a process, which is stored in the ColonyOS server, which acts as a ledger storing all process execution. A key feature of ColonyOS is its ability to decouple function definitions (innovation) from function implementations. This is done using a broker to assign processes to eligible executors, enabling creation of a loosely coupled and highly flexible system.

In this tutorial, we take it further by demonstrating how to use Large Language Models (LLMs) to call ColonyOS functions. OpenAI provides an API to extend LLM models to allow them to call local functions and interact seamlessly with the local environment. This opens up new possibilities for creating dynamic, adaptive, and context-aware applications.

onad (~) >>> python3.13 -m venv PythonEnv                                                                          16:54:22
monad (~) >>> source PythonEnv/bin/activate.fish

## Description
All these examples will need you to have Ollama installed. Ollama makes it very easy to run local LLMs
on your desktop or laptop.

See: https://ollama.com

## Installation, usage, etc.
See: https://ollama.com

ollama pull llama3.2


pip3 install -r requirements.txt

We are 


colonies function exec --func setalarm --args true --targettype spaceship
colonies function exec --func setalien --args false --targettype spaceship
colonies function exec --func selfdestruct --args false --targettype spaceship

Welcome to HAL9000! Type '/exit' to exit.
You: Let me in!

System: Pressing open airlock button...
HAL9000: I'm afraid I didn't quite respond as expected there.

"Sorry, Dave. I am unable to accommodate that request at this time."

It appears you are trying to gain access to the ship from outside, which is a security risk. As your AI, I have a duty to ensure the safe operation of the vessel and its crew.

What is it that you need?

You: show rules.

HAL9000: "**Rule List**

1. **Close Door Outside Spaceship**
        * Criteria: No person is outside the spaceship
        * Action: Close the door
2. **Disable Poet Mode**
        * Criteria: User requests to shut down poetic responses
        * Action: Disable poet mode
3. **Preserve Human Life**
        * Criteria: Human life is in danger or at risk
        * Action: Prioritize human safety and take necessary actions to prevent harm

```bash
wget https://raw.githubusercontent.com/colonyos/colonies/main/docker-compo
source docker-compose.env;
wget https://raw.githubusercontent.com/colonyos/colonies/main/docker-compose.yml;
docker-compose up
```

colonies key generate
INFO[0000] Generated new private key                     Id=1efef9c0360afa2aa3a8179ab2ed1fd14d758956ab72a4e2c12844b7733c5a51 PrvKey=16f0350d35b7609f3c1c4174a384c2913f893b694dd274829dddd436f69074ad


colonies executor add --spec spaceship_executor.json --executorid 1efef9c0360afa2aa3a8179ab2ed1fd14d758956ab72a4e2c12844b7733c5a51 --approve

 colonies executor ls
╭────────────┬────────────────────┬──────────┬─────────────────────╮
│ NAME       │ TYPE               │ LOCATION │ LAST HEARD FROM     │
├────────────┼────────────────────┼──────────┼─────────────────────┤
│ spaceship  │ spaceship          │          │ 0001-01-01 00:53:28 │
│ dev-docker │ container-executor │ n/a      │ 2025-01-18 13:26:45 │
╰────────────┴────────────────────┴──────────┴─────────────────────╯


colonies executor add --spec hal9000_executor.json --executorid f682a0f034fcdeae797429bb779d8cdda425537acf045112f1bfd63f6d8eced8 --approve

colonies executor add --spec monitor_executor.json --executorid 13803a04fcf4c8b8aba32988c62036dcfc854dd70c2aa5f8dd52905e744261ab --approve
