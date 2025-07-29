# LUCA CLI Client

## Overview

The LUCA CLI Client is a command-line interface for your LUCA assistant.

It allows you to interact with an assistant that lives in your terminal.
This is a non-intrusive user experience, that means you still have complete control over your terminal.
But the assistant is always a command away.

## Capabilities

We have designed the system to be able to:
 - Retrieve and search relevant research papers from ArXiv.
 - Retrieve experiments logged in a Weights & Biases project.
 - Generate and execute Python and bash commands.

With these capabilities, you can use the assistant to:
- Generate reports that theorize and summarize your research experiments.
- Generate a project plan to tackle a new research problem.
- Brainstorm, ideate generate new hypotheses based on your current experiments.

## Pre-installation

Before installing the LUCA CLI, please make sure you have created an account on the [LUCA platform](http:myluca.ai).
Additionally, make sure you have exported the `SERVER_URL` environment variable to your local machine.
```bash
export SERVER_URL="http://<your-server-ip>:8000"
```
You can find the `SERVER_URL` in your LUCA account dashboard.


## Installation

```bash
pip install luca-cli
```

## Usage

```bash
luca --help
```
As soon as you pip install the package, please run the following command under any `$ROOT` directory:
```bash
luca init
```
This will initialize the assistant and create a knowledge base `$ROOT/.luca/kb.txt`. \
This knowledge base will be updated with new information as you use the assistant.

After the initialization, you can start interacting with the assistant by just typing your prompt:
```bash
luca "Research papers on reinforcement learning."
```

If you are using Weights & Biases to log your experiments, you can set your \
W&B API key and entity name as environment variables and re-initialize the assistant:
```bash
export WANDB_API_KEY="your-wandb-api-key"
export WANDB_ENTITY="your-wandb-entity"
luca init
```
This will update the assistant and allow the assistant to access your W&B experiments.
You can then do cool things like:

```bash
luca "Export a powerpoint report of all the experiments in my wandb project <your-wandb-project-name>?"
```
You can create reports that theorize and summarize your experiments and help you \
analyze the experiments to come up with better hypotheses for the next set of experiments.
Any file the assistant creates will be synced to your local machine and saved \
in under the `$ROOT/.luca/artifacts` directory.


We plan to significantly expand the set of capabilities of the assistant with each new release. \
Please provide your unfiltered thoughts, suggestions and feedback to us by using the `luca feedback` command.

```bash
luca feedback "I love the assistant!"
```

Cheers, \
The LUCA team
