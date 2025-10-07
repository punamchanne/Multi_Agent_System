

---
title: Multi-Agent AI System
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.7.1
app_file: app_gradio.py
pinned: false
license: mit
---

# 🤖 Multi-Agent AI System

An intelligent AI system that uses multiple specialized agents working together to provide comprehensive answers from various sources.

## 🌟 Features

- **🎯 Controller Agent**: Intelligently routes queries to appropriate specialists
- **📄 PDF RAG Agent**: Analyzes uploaded documents using Retrieval-Augmented Generation
- **🌐 Web Search Agent**: Finds latest information from the internet
- **🎓 ArXiv Agent**: Searches academic papers and research
- **💬 Interactive Chat**: Easy-to-use Gradio interface
- **📚 Sample Documents**: Pre-loaded sample PDFs for testing

## 🚀 How to Use

### 1. Upload Documents
- Click "Upload PDF File" to upload your own documents
- Or select from sample PDFs to get started quickly

### 2. Ask Questions
Type your questions in natural language. The system will automatically:
- Analyze your question
- Choose the best agents to answer it
- Combine responses from multiple sources when needed

### 3. Get Comprehensive Answers
Receive responses that show:
- Which agents were used
- Sources of information
- Combined insights from multiple agents


##  Live Demo & Deployment

### 🌐 Try It Live
Experience the Multi-Agent AI System in action:

[![Open in Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-md-dark.svg)](https://huggingface.co/spaces/punamchanne/multi-agent-ai-system)

**Direct Link**: https://huggingface.co/spaces/punamchanne/multi-agent-ai-system

### ✨ What You Can Do:
- 📄 Upload PDF documents for analysis
- 🤖 Ask questions using multiple AI agents
- 🌐 Get real-time web search results
- 🎓 Access academic papers from ArXiv
- 📊 View system logs and decision-making process

  
## 💡 Example Questions

### PDF-based Questions
- "What is machine learning according to my document?"
- "Summarize the key findings in my uploaded paper"
- "What does the document say about neural networks?"

### Current Information
- "Latest developments in AI this week"
- "Recent breakthroughs in quantum computing"
- "Current trends in renewable energy"

### Academic Research
- "Recent papers on transformer architectures"
- "Latest research in computer vision"
- "Studies on climate change mitigation"

### Multi-source Questions
- "Combine information from my PDF with current research on RAG systems"
- "Compare my document's findings with recent academic papers"

## Project Overview

Multi-Agent System is a smart AI system made up of several "agent" programs that work together to answer your questions. Instead of relying on just one AI, it uses a team of specialists: one for web search, one for PDFs, one for academic papers, and a controller that decides who should answer each question. This makes the answers more accurate and useful, especially for complex or specific queries.

## Architecture & Approach

- **Multi-Agent Design:** The system has four main agents:
  - **Controller Agent:** Decides which specialist(s) to use for each question.
  - **PDF RAG Agent:** Reads and answers questions about uploaded PDF documents.
  - **Web Search Agent:** Finds and summarizes information from the web.
  - **ArXiv Agent:** Searches for and summarizes academic papers.
- **How it works:**
  1. You ask a question (through the web interface).
  2. The Controller Agent analyzes your question and picks the best agent(s).
  3. The chosen agents find answers from their sources.
  4. The Controller combines the answers and sends you a final response.

**Architecture Diagram:**
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Frontend   │    │   Flask API  │    │ Controller  │
│ (Web page)  │◄──►│  (app.py)    │◄──►│   Agent      │
└─────────────┘    └──────────────┘    └─────────────┘
                              │                  │
                              │                  ▼
                              │        ┌────────────────────┐
                              │        │  Agent Router      │
                              │        │  - PDF RAG         │
                              │        │  - Web Search      │
                              │        │  - ArXiv           │
                              │        └────────────────────┘
                              │
                     ┌────────┴────────┐
                     │                 │
              ┌──────▼──────┐  ┌──────▼──────┐
              │   Vector    │  │    Logs     │
              │   Database  │  │   Storage   │
              │  (FAISS)    │  │   (JSON)    │
              └─────────────┘  └─────────────┘
```

## Instructions to Run the Project

### Prerequisites
- Python 3.11 or higher
- Google Gemini API key

### Steps
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd multi agent system
   ```
2. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync
   # Or using pip
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Create a `.env` file in the root directory with:
     ```env
     GEMINI_API_KEY=your_gemini_api_key_here
     ```
4. **(Optional) Generate and ingest sample PDFs:**
   ```bash
   python generate_sample_pdfs.py
   python ingest_sample_pdfs.py
   ```
5. **Run the application:**
   ```bash
   python app.py
   ```
6. **Open the web interface:**
   - Go to `http://localhost:8000` in your browser.

## Dependencies

Main libraries used:
- Flask (web API)
- Flask-CORS (CORS support)
- Google-GenAI (Gemini API)
- FAISS-CPU (vector search)
- DuckDuckGo-Search (web search)
- ArXiv (academic paper search)
- PyMuPDF (PDF reading)
- NumPy (math)
- Python-dotenv (environment variables)

## Dataset Information

- **PDFs:** You can upload your own PDF files through the web interface. Sample PDFs are provided in the `sample_pdfs/` folder. To add more, just upload them or place them in the folder and run the ingestion scripts.
- **Web Data:** The Web Search Agent fetches live data from the internet using DuckDuckGo.
- **Academic Papers:** The ArXiv Agent fetches papers from the ArXiv API in real time.


## Expected Outputs

When you use PixelPrompter, you can expect:

- **Direct answers:**
  - If you ask about something in a PDF you uploaded, you'll get a clear answer from the PDF agent, along with the name of the document.
  - If you ask about current events or general knowledge, the Web Search agent will give you up-to-date information from the internet.
  - If you ask about academic topics, the ArXiv agent will find and summarize relevant research papers.

- **Combined answers:**
  - For complex questions, the system may use more than one agent and combine their answers into a single, easy-to-understand response.

- **Source information:**
  - Every answer includes details about which agent(s) provided the information and where it came from (such as the name of the PDF, website, or research paper).

- **Logs:**
  - All your questions and the system's decisions are saved in the `logs/` folder, so you can review what happened and how answers were found.

+- **Example Outputs:**
  - "According to your uploaded document 'nebulabyte_ai_agents.pdf', machine learning is described as a method where computers learn from data and improve their performance over time without being explicitly programmed for each task."
  - "The latest developments in AI, according to web search, are: 1) The rise of multimodal AI models that can process text, images, and audio together; 2) New breakthroughs in generative AI for creating realistic images and videos; 3) Increased focus on ethical AI and responsible deployment in industry."
  - "Recent papers on transformer architectures include: 1) 'Attention Is All You Need' (Vaswani et al., 2017) – introduces the original transformer model for sequence transduction tasks. 2) 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding' (Devlin et al., 2018) – presents a transformer-based model for language understanding. 3) 'GPT-3: Language Models are Few-Shot Learners' (Brown et al., 2020) – describes a large-scale transformer model for text generation and understanding."
  - "Based on both your PDF and recent web articles, here is a combined answer: Machine learning is a field where computers learn from data, as described in your document 'nebulabyte_ai_agents.pdf'. Recent web articles highlight that the latest trend is using large transformer models, which have enabled significant advances in natural language processing and generative AI."

---

## Example Usage

- Ask: "What does my uploaded document say about machine learning?"
  - The PDF agent will answer, and you'll see the source document.
- Ask: "What are the latest developments in AI?"
  - The Web Search agent will answer with up-to-date info.
- Ask: "Recent papers on transformer architectures"
  - The ArXiv agent will find and summarize academic papers.
- Ask: "Latest research papers on RAG systems and current industry implementations"
  - Multiple agents may work together to give a combined answer.

## Project Structure

```
multi agent system/
├── app.py                    # Main Flask application
├── pyproject.toml           # Project configuration and dependencies
├── .env                     # Environment variables (create this)
├── README.md                # This file
├── generate_sample_pdfs.py  # Script to create sample PDFs
├── ingest_sample_pdfs.py    # Script to ingest sample PDFs
├── rag_index.faiss          # FAISS vector index (generated)
├── rag_index.pkl            # Document metadata (generated)
├── agents/
│   ├── __init__.py
│   ├── controller_agent.py  # Query routing and decision making
│   ├── pdf_rag_agent.py     # PDF processing and RAG
│   ├── web_search_agent.py  # Web search functionality
│   └── arxiv_agent.py       # Academic paper search
├── frontend/
│   └── index.html           # Web interface
├── logs/                    # System logs (generated)
├── uploads/                 # Uploaded PDFs (generated)
└── sample_pdfs/             # Sample documents (generated)
```

## Support

If you have issues:
1. Check the logs in the `/logs` endpoint or the `logs/` folder
2. Review error messages in the web interface
3. Make sure your `.env` file is set up correctly
4. Check your API key permissions

---

**Note:** This is a development project. For production, add more security, rate limiting, and scaling as needed.
