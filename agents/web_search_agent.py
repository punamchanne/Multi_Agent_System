from duckduckgo_search import DDGS
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class WebSearchAgent:
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query, max_results=5):
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
            
            return formatted_results
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
    
    def search_and_summarize(self, query, max_results=5):
        search_results = self.search(query, max_results)
        
        if not search_results or "error" in search_results[0]:
            return {
                "summary": "Unable to perform web search at this time.",
                "results": search_results
            }
        
        context = "\n\n".join([
            f"Source: {r['title']}\nURL: {r['url']}\n{r['snippet']}"
            for r in search_results
        ])
        
        prompt = f"""Based on these web search results, provide a concise summary answering the query: "{query}"

Search Results:
{context}

Summary:"""
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            summary = response.text
        except Exception as e:
            summary = f"Error generating summary: {str(e)}"
        
        return {
            "summary": summary,
            "results": search_results
        }
