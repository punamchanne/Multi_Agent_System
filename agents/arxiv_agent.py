import os
import requests
import google.generativeai as genai
import xml.etree.ElementTree as ET
from urllib.parse import quote

class ArxivAgent:
    def __init__(self):
        pass
    
    def search_papers(self, query, max_results=5):
        try:
            # Get API key from environment
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return "Error: GEMINI_API_KEY not found in environment variables"
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Search ArXiv API
            search_query = quote(query)
            arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results={max_results}"
            
            response = requests.get(arxiv_url, timeout=10)
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.content)
                
                # Extract paper information
                papers = []
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                    summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                    authors = [author.find('{http://www.w3.org/2005/Atom}name').text 
                             for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
                    published = entry.find('{http://www.w3.org/2005/Atom}published').text
                    pdf_link = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    papers.append({
                        'title': title,
                        'authors': ', '.join(authors),
                        'summary': summary,
                        'published': published[:10],  # Just date part
                        'url': pdf_link
                    })
                
                if papers:
                    # Format papers for AI analysis
                    papers_text = ""
                    for i, paper in enumerate(papers, 1):
                        papers_text += f"{i}. {paper['title']}\n"
                        papers_text += f"   Authors: {paper['authors']}\n"
                        papers_text += f"   Published: {paper['published']}\n"
                        papers_text += f"   Summary: {paper['summary'][:300]}...\n"
                        papers_text += f"   URL: {paper['url']}\n\n"
                    
                    # Use AI to provide research summary
                    prompt = f"""
Based on the following ArXiv research papers for the query "{query}":

{papers_text}

Please provide a comprehensive research summary that:
1. Identifies the main themes and findings
2. Highlights the most relevant papers for the query
3. Explains key concepts in accessible language
4. Suggests which papers would be most valuable to read

Be scholarly but accessible in your response.
"""
                    
                    ai_response = model.generate_content(prompt)
                    
                    return f"ArXiv research results for '{query}':\n\n{ai_response.text}\n\nPapers found:\n{papers_text}"
                
                else:
                    return f"No papers found on ArXiv for '{query}'. Try broader or different search terms."
            
            else:
                # Fallback: Use AI for research guidance
                prompt = f"""
The user is looking for research papers about: "{query}"

Please provide helpful guidance about this research topic, including:
1. Key concepts and terminology
2. Important researchers or institutions in this field  
3. Suggested search terms for finding relevant papers
4. Overview of current research directions

Note that ArXiv search is currently unavailable.
"""
                
                ai_response = model.generate_content(prompt)
                return f"Research guidance for '{query}' (ArXiv search unavailable):\n\n{ai_response.text}"
                
        except Exception as e:
            # Fallback: Use AI for research guidance
            try:
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    
                    prompt = f"""
The user is researching: "{query}"

Please provide helpful information about this research topic based on your knowledge.
"""
                    
                    ai_response = model.generate_content(prompt)
                    return f"Research information for '{query}' (ArXiv search error):\n\n{ai_response.text}"
                else:
                    return f"Error searching ArXiv: {str(e)}"
            except:
                return f"Error searching ArXiv and AI fallback: {str(e)}"
