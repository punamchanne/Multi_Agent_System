import os
import json
from datetime import datetime

class ControllerAgent:
    def __init__(self):
        self.logs = []
    
    def analyze_query(self, query, has_pdf=False):
        query_lower = query.lower()
        agents_to_use = []
        
        if has_pdf and any(word in query_lower for word in ["document", "pdf", "file", "uploaded", "content"]):
            agents_to_use.append("PDF_RAG")
        
        if any(word in query_lower for word in ["current", "latest", "news", "recent", "today", "now", "what is", "tell me about"]):
            agents_to_use.append("WEB_SEARCH")
        
        if any(word in query_lower for word in ["paper", "research", "study", "arxiv", "academic", "scientific"]):
            agents_to_use.append("ARXIV")
        
        # If no specific agent matched, default to web search
        if not agents_to_use:
            agents_to_use.append("WEB_SEARCH")
        
        decision = {"agents": agents_to_use, "reasoning": "Rule-based routing"}
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "decision": decision,
            "has_pdf": has_pdf
        }
        self.logs.append(log_entry)
        
        return decision
    
    def get_logs(self):
        return self.logs[-10:]
