# Agentic design patterns

A LangGraph tool-using workflow with a Streamlit chat interface. The reasoning
agent routes arithmetic questions to a calculator and sends other questions to
a general-purpose fallback agent.

## Workflow

```text
Question
	|
Reasoning agent
	|-- arithmetic --> Math agent --> Safe calculator
	`-- other -------> Fallback agent
```

The reasoning agent returns a structured intent and, for arithmetic, an
expression. General questions such as "Define AI" are answered by the fallback
agent instead of being passed to the calculator. The calculator accepts numeric
constants, unary signs, and the `+`, `-`, `*`, `/`, `//`, `%`, and `**`
operators; it does not execute arbitrary Python code.

## Requirements

- Python 3.11 or newer
- An OpenAI API key with access to the configured model

## Setup

From the repository root, create and activate a virtual environment, then
install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```dotenv
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o
```

Keep `.env` private; it is ignored by Git. An `OPENAI_API_KEY` already set in
the process environment takes precedence over the value in `.env`.

## Run the chat app

```powershell
python -m streamlit run streamlit_app.py
```

Streamlit prints the local URL, usually `http://localhost:8501`.

To run the original command-line example instead:

```powershell
python -m patterns.pattern_executer.tool_using.run
```

## Tests

The workflow tests mock the model, so they do not make API requests:

```powershell
python -m unittest discover -s tests
```