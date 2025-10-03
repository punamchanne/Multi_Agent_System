# Multi-Agent AI System

## Overview

This is a multi-agent AI system that intelligently routes user queries to specialized agents based on query content and context. The system features a Flask backend with a web frontend, allowing users to ask questions and upload PDFs for analysis. A controller agent dynamically decides which specialized agent(s) should handle each request, combining their responses when needed.

The system includes four core agents:
- **Controller Agent**: Routes queries using LLM-based decision making and rule-based logic
- **PDF RAG Agent**: Processes uploaded PDFs using FAISS vector search for retrieval-augmented generation
- **Web Search Agent**: Performs real-time web searches using DuckDuckGo
- **ArXiv Agent**: Searches and summarizes academic papers from ArXiv

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: Vanilla HTML/CSS/JavaScript served as static files from Flask

**Design Pattern**: Single-page application with minimal dependencies
- Static files served from `frontend/` directory
- Direct API calls to Flask backend endpoints
- Simple form-based interface for query submission and PDF uploads

**Rationale**: Keeps the system lightweight and deployable without complex build processes. Avoids framework overhead for a minimal UI requirement.

### Backend Architecture

**Framework**: Flask with CORS enabled

**Design Pattern**: Agent-based microservices architecture with centralized routing

**Core Components**:

1. **Controller Agent (agents/controller_agent.py)**
   - Uses Google Gemini API for intelligent query routing
   - Implements hybrid decision-making: LLM analysis + rule-based logic
   - Logs all routing decisions with timestamps and rationale
   - Returns structured JSON responses indicating which agents to invoke
   - **Rationale**: Combining LLM flexibility with rule-based reliability ensures both intelligent routing and predictable behavior for clear-cut cases

2. **PDF RAG Agent (agents/pdf_rag_agent.py)**
   - PDF text extraction using PyMuPDF (fitz)
   - Text chunking with configurable overlap (default: 500 words, 50-word overlap)
   - Vector embeddings via Google's text-embedding-004 model
   - FAISS IndexFlatL2 for similarity search
   - Persistent storage via pickle and FAISS index files
   - **Rationale**: FAISS provides fast, in-memory vector search without external database dependencies. Chunking with overlap prevents context loss at boundaries.

3. **Web Search Agent (agents/web_search_agent.py)**
   - DuckDuckGo search integration via duckduckgo-search library
   - Summarization of search results using Gemini
   - Structured response format with URLs and snippets
   - **Rationale**: DuckDuckGo avoids API key requirements and rate limits compared to commercial search APIs while providing adequate results

4. **ArXiv Agent (agents/arxiv_agent.py)**
   - Python arxiv library for academic paper search
   - Sorts by submission date for recent papers
   - LLM-based summarization of multiple paper abstracts
   - **Rationale**: Direct API access to ArXiv provides reliable academic content without scraping

**Request Flow**:
1. User submits query via frontend
2. Backend routes to controller agent
3. Controller analyzes query and decides agent(s) to invoke
4. Selected agents execute in sequence or parallel
5. Responses aggregated and returned to frontend
6. Decision trace logged to JSON files

**File Upload Handling**:
- Secure filename validation using werkzeug
- 16MB file size limit
- PDF-only restriction via extension checking
- Files stored in `uploads/` directory
- Automatic ingestion into RAG vector store

**Logging Strategy**:
- JSON-formatted logs in `logs/` directory
- Daily log files with timestamp naming
- Captures: query, decision rationale, agents used, responses, and timing
- Enables auditability and system debugging

### Data Storage Solutions

**Vector Store**: FAISS (Facebook AI Similarity Search)
- In-memory index with file-based persistence
- IndexFlatL2 for exact L2 distance search
- 768-dimensional embeddings (matching Google's embedding model)
- Metadata stored separately in pickle format
- **Pros**: Fast retrieval, no external dependencies, simple deployment
- **Cons**: Not distributed, limited to single-machine memory, no concurrent write support
- **Alternatives considered**: Chroma (more features but additional dependency), Pinecone (cloud-based but requires subscription)

**Document Storage**:
- Local filesystem for uploaded PDFs
- Pickle files for document metadata and chunks
- JSON files for request logs
- **Rationale**: Simple deployment without database setup; suitable for moderate document volumes

### Authentication and Authorization

**Current Implementation**: None

**Security Measures**:
- File upload validation (type, size)
- Secure filename handling
- CORS configuration for frontend access
- **Note**: This is a demonstration system; production deployment would require authentication, rate limiting, and user isolation

### LLM Integration Strategy

**Provider**: Google Gemini API (genai library)

**Models Used**:
- `gemini-2.5-flash`: Controller routing and response synthesis
- `text-embedding-004`: Document embeddings for RAG

**API Client Pattern**:
- Single shared client instance initialized with API key from environment
- Structured prompts with system instructions
- JSON-mode responses for controller decisions
- **Rationale**: Google AI Studio offers generous free tier, fast response times, and strong reasoning capabilities for routing decisions

**Configuration**:
- API keys loaded from environment variables
- No hardcoded credentials
- Supports deployment to cloud platforms with environment management

## External Dependencies

### Third-Party APIs

1. **Google Gemini API (genai)**
   - Purpose: LLM-based routing decisions and content generation
   - Authentication: API key via `GEMINI_API_KEY` environment variable
   - Rate limits: Free tier has daily request limits
   - Fallback: System degrades to rule-based routing if API unavailable

2. **DuckDuckGo Search**
   - Purpose: Real-time web search results
   - Authentication: None required
   - Rate limits: Implicit rate limiting; handled gracefully with try/catch
   - Library: `duckduckgo-search`

3. **ArXiv API**
   - Purpose: Academic paper search and metadata
   - Authentication: None required
   - Library: `arxiv` (official Python client)
   - Rate limits: Respectful usage enforced by library

### Python Libraries

**Core Framework**:
- `Flask`: Web server and routing
- `flask-cors`: Cross-origin resource sharing support

**Agent Libraries**:
- `google-genai`: Google AI SDK for Gemini access
- `arxiv`: ArXiv API client
- `duckduckgo-search`: Web search functionality
- `PyMuPDF` (fitz): PDF text extraction
- `faiss-cpu`: Vector similarity search
- `numpy`: Numerical operations for embeddings

**Utilities**:
- `werkzeug`: Secure file handling
- Standard library: `os`, `json`, `datetime`, `pickle`

### Development Tools

**PDF Generation**:
- `generate_sample_pdfs.py`: Creates sample NebulaByte domain PDFs for testing
- `ingest_sample_pdfs.py`: Batch ingests PDFs into RAG system

**Deployment Requirements**:
- Environment variable support for API keys
- Write access to `uploads/` and `logs/` directories
- File system persistence for FAISS indices

### Infrastructure Considerations

**Deployment Targets**: Designed for Render, Heroku, or Hugging Face Spaces

**Resource Requirements**:
- Minimal CPU for API-based LLM calls
- Memory for FAISS index (scales with document count)
- Disk space for uploaded PDFs and log retention

**Environment Variables Required**:
- `GEMINI_API_KEY`: Google AI Studio API key (required)