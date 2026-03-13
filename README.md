# Weather & News Assistant

A conversational AI assistant that fetches real-time weather and top news stories, built with the **Model Context Protocol (MCP)**.

## Architecture

```
┌──────────────┐     OpenAI API      ┌─────────────────────┐
│  Streamlit   │ ─── gpt-4.1-mini ──▶│    Agent (agent.py) │
│  (app.py)    │ ◀──────────────────  │   MCP tool-use loop │
└──────────────┘                      └────────┬────────────┘
                                               │ MCP stdio
                              ┌────────────────┴────────────────┐
                              │                                   │
                     ┌────────▼────────┐              ┌──────────▼────────┐
                     │  weather_server │              │   news_server     │
                     │  Open-Meteo API │              │  Hacker News API  │
                     │  (no API key)   │              │  (no API key)     │
                     └─────────────────┘              └───────────────────┘
```

## Components

| File | Role |
|---|---|
| `app.py` | Streamlit chat UI |
| `agent.py` | OpenAI agent loop + MCP client |
| `weather_server.py` | MCP server — current weather via Open-Meteo |
| `news_server.py` | MCP server — top stories via Hacker News |

## Setup

**1. Install dependencies**
```bash
pip install -r dependencies.txt
```

**2. Add your OpenAI API key**
```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

**3. Run the app**
```bash
streamlit run app.py
```

## Example Queries

- *"What's the weather in Tokyo?"*
- *"Show me the top 5 news stories"*
- *"What's the weather in London and the latest tech news?"*

## Data Sources

- **Weather** — [Open-Meteo](https://open-meteo.com/) (free, no API key)
- **News** — [Hacker News API](https://github.com/HackerNews/API) (free, no API key)
- **LLM** — OpenAI `gpt-4.1-mini` (API key required)
