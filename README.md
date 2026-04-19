# HDFC MF FAQ Assistant
> Facts-only Mutual Fund FAQ assistant powered by RAG (Retrieval-Augmented Generation)  
> Built for Groww | AMC: HDFC Mutual Fund

---

## What it does
Answers factual questions about HDFC Mutual Fund schemes available 
on Groww — such as expense ratio, exit load, minimum SIP, lock-in 
period, riskometer, benchmark index, and how to download statements.

Every answer includes one cited source link. Opinionated or 
portfolio questions are politely refused with an educational link.

---

## Schemes Covered
| Scheme | Category |
|--------|----------|
| HDFC Top 100 Fund | Large Cap · Equity |
| HDFC Flexi Cap Fund | Flexi Cap · Equity |
| HDFC ELSS Tax Saver Fund | ELSS · Tax Saving |
| HDFC Mid Cap Opportunities Fund | Mid Cap · Equity |
| HDFC Small Cap Fund | Small Cap · Equity |
| HDFC Balanced Advantage Fund | Hybrid · Balanced Advantage |
| HDFC Nifty 50 Index Fund | Index · Passive |

---

## Tech Stack
| Component | Technology |
|-----------|------------|
| UI | Streamlit |
| Vector DB | ChromaDB (persistent, local) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Scraping | requests + BeautifulSoup4 |
| Chunking | LangChain RecursiveCharacterTextSplitter |

---

## Setup Steps

### 1. Clone and navigate
```bash
cd hdfc-mf-faq
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
pip install langchain-text-splitters groq
```

### 3. Set up environment
```bash
copy .env.example .env
# Open .env and add your Groq API key:
# GROQ_API_KEY=your_key_here
# Get free key at: https://console.groq.com/keys
```

### 4. Build the knowledge base
```bash
python -c "from src.ingest import ingest_knowledge_base; ingest_knowledge_base('data/chroma_db')"
```

### 5. Run the app
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Project Structure
hdfc-mf-faq/
├── app.py                  # Streamlit UI
├── src/
│   ├── ingest.py           # Scraping + chunking + embedding pipeline
│   ├── rag.py              # Retrieval + Groq LLM call
│   ├── prompts.py          # System prompt, refusal logic, disclaimer
│   ├── knowledge_base.py   # Hardcoded verified facts (49 entries)
│   └── utils.py            # Helpers
├── data/
│   ├── sources.csv         # 20 verified source URLs
│   ├── chroma_db/          # ChromaDB vector store (auto-created)
│   └── FILL_SOURCES_MANUALLY.md
├── sample_qa.md            # 10 sample Q&As with answers + links
├── requirements.txt
├── .env.example
└── README.md

---

## Source Corpus
- **Total URLs:** 28 verified public pages
- **Sources:** HDFC AMC, Groww, AMFI, SEBI
- **Full list:** see `data/sources.csv` 

---

## Known Limits
- Knowledge base is static (hardcoded facts as of April 2026)
- TER/expense ratios change periodically — always verify at hdfcfund.com
- PDF documents (SID/KIM) are skipped during scraping due to size
- App runs locally only — no cloud hosting configured
- No PII collected or stored at any point

---

## Disclaimer
⚠️ Facts-only assistant. No investment advice provided.
Mutual fund investments are subject to market risks.
Please read all scheme-related documents carefully before investing.
For advice, consult a SEBI-registered investment advisor.

---

## Deliverables Checklist
- [x] Working prototype (Streamlit app)
- [x] Source list (data/sources.csv — 20 URLs)
- [x] README with setup steps
- [x] Sample Q&A file (sample_qa.md — 10 queries)
- [x] Disclaimer in UI and in README
