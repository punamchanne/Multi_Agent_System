import os
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
import time

class WebSearchAgent:
    def __init__(self):
        pass
    
    def search(self, query, max_results=5):
        try:
            # Get API key from environment
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return "Error: GEMINI_API_KEY not found in environment variables"
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Use DuckDuckGo search (no API key required)
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract search results
                results = []
                result_elements = soup.find_all('div', class_='result')[:max_results]
                
                for element in result_elements:
                    title_element = element.find('a', class_='result__a')
                    snippet_element = element.find('a', class_='result__snippet')
                    
                    if title_element and snippet_element:
                        title = title_element.get_text().strip()
                        snippet = snippet_element.get_text().strip()
                        url = title_element.get('href', '')
                        
                        results.append({
                            'title': title,
                            'snippet': snippet,
                            'url': url
                        })
                
                if results:
                    # Format results for AI summarization
                    search_results_text = ""
                    for i, result in enumerate(results, 1):
                        search_results_text += f"{i}. {result['title']}\n"
                        search_results_text += f"   {result['snippet']}\n"
                        search_results_text += f"   URL: {result['url']}\n\n"
                    
                    # Use AI to provide a comprehensive summary
                    prompt = f"""
Based on the following web search results for the query "{query}":

{search_results_text}

Please provide a comprehensive, informative summary that answers the user's query. Include the most relevant information from the search results and mention key sources when appropriate.
"""
                    
                    ai_response = model.generate_content(prompt)
                    
                    return f"Web search results for '{query}':\n\n{ai_response.text}\n\nSources:\n{search_results_text}"
                
                else:
                    return f"No search results found for '{query}'. Please try a different query."
            
            else:
                # Fallback: Use AI to provide general knowledge response
                prompt = f"""
The user asked about: "{query}"

Please provide a helpful, informative response based on your knowledge. Make it clear that this is based on general knowledge rather than current web search results.
"""
                
                ai_response = model.generate_content(prompt)
                return f"Based on general knowledge (web search unavailable): {ai_response.text}"
                
        except Exception as e:
            # Fallback: Use AI for general knowledge
            try:
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    
                    prompt = f"""
The user asked: "{query}"

Please provide a helpful response based on your knowledge. Note that real-time web search is currently unavailable.
"""
                    
                    ai_response = model.generate_content(prompt)
                    return f"Response based on AI knowledge (web search error): {ai_response.text}"
                else:
                    return f"Error performing web search: {str(e)}"
            except:
                return f"Error performing web search and AI fallback: {str(e)}"
