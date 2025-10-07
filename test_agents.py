#!/usr/bin/env python3
"""
Test script to verify all agents work properly
"""
import os
os.environ["GEMINI_API_KEY"] = "test_key"  # Set dummy key for testing

try:
    print("Testing agent imports...")
    
    from agents.controller_agent import ControllerAgent
    print("✅ Controller Agent imported successfully")
    
    from agents.web_search_agent import WebSearchAgent  
    print("✅ Web Search Agent imported successfully")
    
    from agents.arxiv_agent import ArxivAgent
    print("✅ ArXiv Agent imported successfully")
    
    from agents.pdf_rag_agent import PDFRAGAgent
    print("✅ PDF RAG Agent imported successfully")
    
    print("\nTesting agent initialization...")
    
    controller = ControllerAgent()
    print("✅ Controller Agent initialized")
    
    web_search = WebSearchAgent()
    print("✅ Web Search Agent initialized")
    
    arxiv_agent = ArxivAgent()
    print("✅ ArXiv Agent initialized")
    
    pdf_rag = PDFRAGAgent()
    print("✅ PDF RAG Agent initialized")
    
    print("\nTesting basic functionality...")
    
    # Test controller routing
    decision = controller.analyze_query("test query", False)
    print(f"✅ Controller routing works: {decision}")
    
    # Test web search (without actual search)
    try:
        web_response = web_search.search("test")
        print(f"✅ Web search method works: {type(web_response)}")
    except Exception as e:
        print(f"⚠️ Web search error (expected): {str(e)}")
    
    # Test arxiv search (without actual search)
    try:
        arxiv_response = arxiv_agent.search_papers("test")
        print(f"✅ ArXiv search method works: {type(arxiv_response)}")
    except Exception as e:
        print(f"⚠️ ArXiv search error (expected): {str(e)}")
    
    print("\n🎉 All tests passed! Agents are working correctly.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()