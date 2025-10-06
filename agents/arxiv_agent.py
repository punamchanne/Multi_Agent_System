import arxiv
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class ArxivAgent:
    def __init__(self):
        self.client = arxiv.Client()
    
    def search_papers(self, query, max_results=5):
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            for result in self.client.results(search):
                papers.append({
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "url": result.entry_id,
                    "pdf_url": result.pdf_url
                })
            
            return papers
        except Exception as e:
            return [{"error": f"ArXiv search failed: {str(e)}"}]
    
    def search_and_summarize(self, query, max_results=5):
        papers = self.search_papers(query, max_results)
        
        if not papers or "error" in papers[0]:
            return {
                "summary": "Unable to search ArXiv at this time.",
                "papers": papers
            }
        
        context = "\n\n".join([
            f"Title: {p['title']}\nAuthors: {', '.join(p['authors'][:3])}\nPublished: {p['published']}\nAbstract: {p['summary'][:500]}..."
            for p in papers
        ])
        
        prompt = f"""Based on these recent ArXiv papers, provide a summary related to the query: "{query}"

Papers:
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
            "papers": papers
        }
