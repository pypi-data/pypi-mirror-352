> [!IMPORTANT]  
> This repository has been merged into the [Kozmograph AI Toolkit](https://github.com/kozmograph/ai-toolkit) monorepo to avoid duplicating tools.  
> It will be deleted in one month—please follow the [Langchain integration](https://github.com/kozmograph/ai-toolkit/tree/main/integrations/langchain-kozmograph) there for all future development, and feel free to open issues or PRs in that repo.

# 🦜️🔗 LangChain Kozmograph

This package contains the LangChain integration with [Kozmograph](https://kozmograph.com/) graph database.

## 📦 Installation

```bash
pip install -U langchain-kozmograph
```

## 💻 Integration features

### Kozmograph

The `Kozmograph` class is a wrapper around the database client that supports the 
query operation. 

```python
import os
from langchain_kozmograph.graphs.kozmograph import Kozmograph

url = os.getenv("KOZMOGRAPH_URI", "bolt://localhost:7687")
username = os.getenv("KOZMOGRAPH_USERNAME", "")
password = os.getenv("KOZMOGRAPH_PASSWORD", "")

graph = Kozmograph(url=url, username=username, password=password, refresh_schema=False)
results = graph.query("MATCH (n) RETURN n LIMIT 1")
print(results)
```

### KozmographQAChain

The `KozmographQAChain` class enables natural language interactions with a Kozmograph database. 
It uses an LLM and the database's schema to translate a user's question into a Cypher query, which is executed against the database.
The resulting data is then sent along with the user's question to the LLM to generate a natural language response.

```python
import os
from langchain_kozmograph.graphs.kozmograph import Kozmograph
from langchain_kozmograph.chains.graph_qa import KozmographQAChain
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
url = os.getenv("KOZMOGRAPH_URI", "bolt://localhost:7687")
username = os.getenv("KOZMOGRAPH_USERNAME", "")
password = os.getenv("KOZMOGRAPH_PASSWORD", "")

graph = Kozmograph(url=url, username=username, password=password, refresh_schema=False)

chain = KozmographQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=graph,
    model_name="gpt-4-turbo",
    allow_dangerous_requests=True,
)
response = chain.invoke("Is there a any Person node in the dataset?")
result = response["result"].lower()
print(result)
```

### Kozmograph toolkit

The `KozmographToolkit` contains different tools agents can leverage to perform specific tasks the user has given them. Toolkit 
needs a database object and LLM access since different tools leverage different operations.  

Currently supported tools: 

1. **QueryKozmographTool** - Basic Cypher query execution tool


```python
import os
import pytest
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_kozmograph import KozmographToolkit
from langchain_kozmograph.graphs.kozmograph import Kozmograph
from langgraph.prebuilt import create_react_agent

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
url = os.getenv("KOZMOGRAPH_URI", "bolt://localhost:7687")
username = os.getenv("KOZMOGRAPH_USERNAME", "")
password = os.getenv("KOZMOGRAPH_PASSWORD", "")

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

db = Kozmograph(url=url, username=username, password=password)
toolkit = KozmographToolkit(db=db, llm=llm)

agent_executor = create_react_agent(
    llm, toolkit.get_tools(), prompt="You will get a cypher query, try to execute it on the Kozmograph database."
)

example_query = "MATCH (n) WHERE n.name = 'Jon Snow' RETURN n"
events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)

last_event = None
for event in events:
    last_event = event
    event["messages"][-1].pretty_print()

print(last_event)

```

## 🧪 Test

Install the test dependencies to run the tests:
1. Install dependencies 

```bash
poetry install --with test,test_integration
```

2. Start Kozmograph in the background. 
   
3. Create an `.env` file that points to Kozmograph and OpenAI API
```
KOZMOGRAPH_URI=bolt://localhost:7687
KOZMOGRAPH_USERNAME=
KOZMOGRAPH_PASSWORD=
OPENAI_API_KEY=your_openai_api_key
```

### Run tests 

Run the unit tests using:

```bash
make tests
```

Run the integration test using: 

 ```bash
 make integration_tests
 ```

## 🧹 Code Formatting and Linting

Install the `codespell`, `lint`, and typing dependencies to lint and format your code:

```bash
poetry install --with codespell,lint,typing
```

To format your code, run:

```bash
make format
```

To lint it, run:

```bash
make lint
```