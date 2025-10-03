import fitz
import os

os.makedirs('sample_pdfs', exist_ok=True)

sample_dialogs = [
    {
        "filename": "nebulabyte_ai_agents.pdf",
        "title": "NebulaByte: Introduction to AI Agents",
        "content": """NebulaByte AI Agents Guide

What are AI Agents?
AI agents are autonomous systems capable of perceiving their environment and taking actions to achieve specific goals. Unlike traditional software, AI agents can:
- Learn from experience
- Adapt to new situations
- Make decisions based on context
- Interact with users naturally

Key Components:
1. Perception: Gathering information from the environment
2. Reasoning: Processing information to make decisions
3. Action: Executing tasks based on decisions
4. Learning: Improving performance over time

Types of AI Agents:
- Reactive Agents: Respond to immediate stimuli
- Deliberative Agents: Plan actions based on goals
- Hybrid Agents: Combine reactive and deliberative approaches
- Multi-Agent Systems: Multiple agents working together

Applications:
AI agents are used in customer service, autonomous vehicles, game playing, personal assistants, and industrial automation. They represent the future of intelligent automation."""
    },
    {
        "filename": "nebulabyte_rag_systems.pdf",
        "title": "NebulaByte: Retrieval-Augmented Generation",
        "content": """NebulaByte RAG Systems Documentation

Understanding RAG
Retrieval-Augmented Generation (RAG) is a technique that enhances LLMs by providing them with relevant external knowledge. This approach combines the benefits of:
- Large language models' natural language understanding
- External knowledge bases for factual accuracy
- Real-time information retrieval

RAG Architecture:
1. Document Ingestion: Convert documents to text
2. Chunking: Break text into manageable pieces
3. Embedding: Convert chunks to vector representations
4. Indexing: Store embeddings in a vector database
5. Retrieval: Find relevant chunks for queries
6. Generation: Use LLM to generate answers

Benefits:
- Improved factual accuracy
- Reduced hallucinations
- Domain-specific knowledge
- Up-to-date information
- Cost-effective compared to fine-tuning

Implementation Strategies:
Use FAISS or Chroma for vector storage, sentence-transformers for embeddings, and GPT or Claude for generation. Consider chunk size, overlap, and retrieval strategies."""
    },
    {
        "filename": "nebulabyte_vector_databases.pdf",
        "title": "NebulaByte: Vector Database Guide",
        "content": """NebulaByte Vector Database Technologies

What are Vector Databases?
Vector databases store and retrieve high-dimensional vector embeddings efficiently. They enable similarity search, which is fundamental for:
- Semantic search
- Recommendation systems
- RAG applications
- Image and video search

Popular Vector Databases:
1. FAISS: Facebook's library for efficient similarity search
2. Chroma: Open-source embedding database
3. Pinecone: Managed vector database service
4. Weaviate: Open-source vector search engine
5. Milvus: Cloud-native vector database

Key Concepts:
- Embeddings: Numerical representations of data
- Distance Metrics: Cosine similarity, Euclidean distance
- Indexing: Optimizing search performance
- Dimensionality: Typical ranges from 384 to 1536

FAISS Features:
FAISS provides multiple index types including IndexFlatL2 for exact search, IndexIVFFlat for faster approximate search, and IndexHNSW for hierarchical navigable small world graphs."""
    },
    {
        "filename": "nebulabyte_llm_apis.pdf",
        "title": "NebulaByte: LLM API Integration",
        "content": """NebulaByte LLM API Integration Guide

Working with LLM APIs
Modern applications leverage Large Language Models through APIs provided by various vendors. Key considerations:

Major Providers:
1. OpenAI: GPT-4, GPT-3.5 with strong reasoning
2. Anthropic: Claude with long context windows
3. Google: Gemini with multimodal capabilities
4. Groq: Ultra-fast inference speeds
5. Cohere: Specialized for enterprise use

API Integration Best Practices:
- Use environment variables for API keys
- Implement rate limiting and retries
- Handle errors gracefully
- Monitor usage and costs
- Cache responses when appropriate

Prompt Engineering:
Effective prompts include clear instructions, relevant context, examples when needed, and structured output formats. Consider system prompts for consistent behavior.

Cost Optimization:
- Choose appropriate model sizes
- Use streaming for real-time responses
- Batch requests when possible
- Implement caching strategies
- Monitor token usage

Security:
Never hardcode API keys, use secret management systems, validate inputs, sanitize outputs, and implement usage limits."""
    },
    {
        "filename": "nebulabyte_multiagent_systems.pdf",
        "title": "NebulaByte: Multi-Agent System Design",
        "content": """NebulaByte Multi-Agent Systems Architecture

Introduction to Multi-Agent Systems
Multi-agent systems consist of multiple autonomous agents that coordinate to solve complex problems. This approach offers:
- Modularity: Each agent handles specific tasks
- Scalability: Easy to add new capabilities
- Robustness: Failure of one agent doesn't crash system
- Specialization: Agents optimize for specific domains

Controller Patterns:
1. Centralized: Single controller routes all requests
2. Decentralized: Agents negotiate directly
3. Hierarchical: Multiple levels of control
4. Hybrid: Combine approaches based on needs

Agent Communication:
Agents exchange information through:
- Message passing
- Shared memory
- Event systems
- REST APIs

Routing Strategies:
- Rule-based: Use explicit conditions
- LLM-based: Let AI decide routing
- Hybrid: Combine rules with AI reasoning
- Learned: Use ML to optimize routing

Common Agent Types:
- Information Retrieval: Search and fetch data
- Processing: Transform and analyze information
- Decision Making: Choose actions based on context
- Execution: Carry out selected actions

Design Considerations:
Consider failure modes, logging for transparency, performance optimization, and user experience when building multi-agent systems."""
    }
]

for dialog in sample_dialogs:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    
    text = f"{dialog['title']}\n\n{dialog['content']}"
    
    rect = fitz.Rect(50, 50, 545, 792)
    page.insert_textbox(rect, text, fontsize=11, fontname="helv", align=0)
    
    filepath = os.path.join('sample_pdfs', dialog['filename'])
    doc.save(filepath)
    doc.close()
    print(f"Created {filepath}")

print("\nAll sample PDFs created successfully!")
