# Multi-Agent Research System (ResearchMind)

An autonomous multi-agent AI research pipeline that discovers, reads, synthesizes, and critiques in-depth research reports on any topic using OpenAI and Tavily.

---

## Architecture Overview

```
                      +-------------------+
                      |   User Query      |
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |  1. Search Agent  |  <-- Tavily Web Search
                      +---------+---------+
                                | Top URLs & snippets
                                v
                      +-------------------+
                      |  2. Reader Agent  |  <-- BeautifulSoup Scraper
                      +---------+---------+
                                | Full text & context
                                v
                      +-------------------+
                      |  3. Writer Chain  |  <-- GPT-4o-mini structured report
                      +---------+---------+
                                | Draft report
                                v
                      +-------------------+
                      |  4. Critic Chain  |  <-- Evaluation (Score, Strengths, Verdict)
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      | Final Output / UI |  (Streamlit / Terminal)
                      +-------------------+
```

### Agents & Chains Breakdown

1. **Search Agent (`build_search_agent`)**:
   - Queries the web via Tavily Search API.
   - Retrieves top source URLs, titles, and snippets.

2. **Reader Agent (`build_reader_agent`)**:
   - Extracts and parses text content from the most promising source URLs using BeautifulSoup.
   - Cleans HTML, stripping unnecessary scripts, styles, navigation, and footers.

3. **Writer Chain (`writer_chain`)**:
   - Synthesizes findings into a professional research report with:
     - Executive Introduction
     - Key Findings (with detailed explanations)
     - Conclusion & Implications
     - Cited Sources

4. **Critic Chain (`critic_chain`)**:
   - Evaluates the report for depth, accuracy, clarity, and factual completeness.
   - Outputs a Score (/10), Strengths, Improvement Areas, and a Verdict.

---

## Project Structure

```
Multi-agent-research-system/
├── agents.py           # Agent definitions (Search, Reader, Writer, Critic)
├── tools.py            # Web search (Tavily) & web scraper (BeautifulSoup) tools
├── pipeline.py         # End-to-end multi-agent orchestration pipeline
├── app.py              # Interactive Streamlit dashboard
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable templates
└── .gitignore          # Git exclusion rules
```

---

## Getting Started

### 1. Installation

Create and activate a virtual environment, then install dependencies:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the folder:

```bash
cp .env.example .env
```

Add your API keys:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

---

## Running the Application

### Option A: Streamlit Interactive Web App

Launch the full-featured dashboard:

```bash
streamlit run app.py
```

### Option B: Terminal Pipeline

Run directly in Python:

```python
from pipeline import run_research_pipeline

result = run_research_pipeline("Quantum Computing Breakthroughs 2026")
print(result["report"])
print(result.get("critique", ""))
```
