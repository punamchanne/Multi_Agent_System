#!/usr/bin/env python3
"""
Quick test script to verify web search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from agents.web_search_agent import WebSearchAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_web_search():
    print("Testing Web Search Agent...")
    
    # Initialize the agent
    agent = WebSearchAgent()
    
    # Test query
    test_query = "latest AI news"
    print(f"Query: {test_query}")
    
    try:
        # Test search functionality
        results = agent.search_and_summarize(test_query, max_results=3)
        
        print("\n=== Search Results ===")
        print(f"Summary: {results.get('summary', 'No summary')}")
        
        if 'results' in results and results['results']:
            print(f"\nFound {len(results['results'])} results:")
            for i, result in enumerate(results['results'][:3], 1):
                if 'error' in result:
                    print(f"{i}. ERROR: {result['error']}")
                else:
                    print(f"{i}. {result.get('title', 'No title')}")
                    print(f"   URL: {result.get('url', 'No URL')}")
                    print(f"   Snippet: {result.get('snippet', 'No snippet')[:100]}...")
        else:
            print("No results found or error occurred")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_search()