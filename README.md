# HKÜ RAG Chatbot

🔗 **Live demo:**    https://hku-rag-chatbot.vercel.app/

> Note: hosted on a free tier, so the first request may take 30-60s to wake the server.


**Evaluation:** Faithfulness 5.0/5 · Answer Relevancy 5.0/5 (measured with an LLM-as-a-judge pipeline on a test set of core questions)

2. Tech Stack bölümünü güncelle — eski bilgiler duruyor, düzelt:

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about the Computer Engineering department of Hasan Kalyoncu University, using real data scraped from the department website.

Built end-to-end as a learning project: web scraping → data cleaning → chunking → embeddings → vector search → LLM generation → API → web interface.

---

## What it does

Users can ask questions in Turkish like:
- "Is there an Artificial Intelligence course?"
- "Who is the head of the department?"
- "How many credits are required to graduate?"
- "Which professors are in the department?"

The system finds the relevant information from the university's real data and generates an accurate answer — **with clickable source links** to the original pages. If it doesn't know, it says so instead of making things up.

---

## Architecture

The project is built in layers:

1. **Data collection** — Web scraping with `requests` + `BeautifulSoup` (crawls the department site, cleans navigation/footer noise)
2. **Data preparation** — Text chunking with LangChain's `RecursiveCharacterTextSplitter`
3. **Retrieval** — Multilingual embeddings (Google Gemini (gemini-embedding-001)) stored in `ChromaDB`
4. **Generation** — LLM answers via `Ollama` (`qwen2.5`), grounded in retrieved context
5. **API** — `FastAPI` service exposing a `/sor` endpoint
6. **Interface** — A custom HTML/CSS/JavaScript chat UI with source citations

---

## Tech Stack

- **Language:** Python, JavaScript
- **Scraping:** requests, BeautifulSoup
- **RAG:** LangChain (text splitting), sentence-transformers, ChromaDB
- **LLM:** Groq (Llama 3.3 70B)
- **Backend:** FastAPI, Uvicorn
- **Frontend:** HTML, CSS, JavaScript
 Deployment: Backend on Render, frontend on Vercel
 Evaluation: Custom LLM-as-a-judge pipeline

---

## How to run

Create a `.env` file with:
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key



## Key engineering decisions

This project was as much about **debugging** as building. Some problems I solved:

- **Weak retrieval → stronger embeddings.** The first model (MiniLM) couldn't match Turkish queries to the right content. Switching to `multilingual-e5-large` dropped distance scores from 0.41 to 0.14.
- **Hallucination → distance threshold.** The system was inventing answers for questions outside its data. I added a distance threshold: if the closest chunk is too far, it returns "I don't have information" without calling the LLM.
- **Noisy data → whitelist filtering.** Instead of chasing junk files one by one, I switched to a whitelist of high-value pages. 278 chunks → 71 clean chunks.
- **Language mixing → model switch.** The small LLM mixed English/Turkish. Since it was a model limitation (not a prompt issue), I switched to `qwen2.5`.
- **Structured data → single-chunk strategy.** The academic staff list was getting split and mixed up, so I kept it as one chunk and added search-friendly keywords to improve retrieval.

---
## Evaluation

I built a lightweight LLM-as-a-judge evaluation pipeline (`degerlendir.py`) that scores each answer on two metrics:
- **Faithfulness:** is the answer grounded only in the retrieved context?
- **Answer Relevancy:** how relevant is the answer to the question?

On a test set of core questions, the system scored 5.0/5 on both. The test set covers questions with known answers in the data; edge cases (partial or missing answers) would be the next step to expand coverage.

## Known limitations

- **Counting/filtering questions** ("how many professors are there?") can be inaccurate — RAG works on semantic similarity, not exact counting.
- **Data is a snapshot** — if the website changes, the bot may become outdated until re-scraped.

---

## What's next

- Hybrid search (semantic + keyword) for exact codes/names
- Reranking for better result ordering
- Evaluation metrics to measure accuracy
- Agentic RAG — letting the model decide when to search


---

## Author

Built by [Eren](https://github.com/erenogan)

*This project represents the "RAG" stage of my learning path: ML → Deep Learning → NLP → Transformers → RAG → AI Agents.*
