import os
import json
from datetime import datetime
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class ControllerAgent:
    def __init__(self):
        self.decision_log = []
    
    def analyze_query(self, query, has_pdf_upload=False):
        system_prompt = """You are a query routing controller for a multi-agent AI system. 
Analyze the user query and decide which agent(s) to call:
- PDF_RAG: Use when query asks about uploaded PDF content or document analysis
- WEB_SEARCH: Use for recent news, current events, latest information, or general web queries
- ARXIV: Use when query mentions papers, research, arxiv, or academic content
- MULTIPLE: Use multiple agents if query spans multiple domains

Respond in JSON format:
{
  "agents": ["AGENT_NAME1", "AGENT_NAME2"],
  "rationale": "Brief explanation of why these agents were chosen",
  "priority": "primary_agent_name"
}"""

        query_context = f"Query: {query}\nPDF uploaded: {has_pdf_upload}"
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=query_context)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                ),
            )
            
            decision = json.loads(response.text or "{}")
            
            self._apply_rule_based_logic(query, has_pdf_upload, decision)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "has_pdf": has_pdf_upload,
                "decision": decision,
                "method": "LLM + rules"
            }
            self.decision_log.append(log_entry)
            
            return decision
            
        except Exception as e:
            fallback_decision = self._fallback_routing(query, has_pdf_upload)
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "has_pdf": has_pdf_upload,
                "decision": fallback_decision,
                "method": "fallback_rules",
                "error": str(e)
            }
            self.decision_log.append(log_entry)
            return fallback_decision
    
    def _apply_rule_based_logic(self, query, has_pdf_upload, decision):
        query_lower = query.lower()
        
        if has_pdf_upload and "PDF_RAG" not in decision["agents"]:
            decision["agents"].insert(0, "PDF_RAG")
            decision["rationale"] += " [Rule: PDF uploaded, added PDF_RAG]"
        
        if any(keyword in query_lower for keyword in ["recent", "latest", "news", "today", "current"]):
            if "WEB_SEARCH" not in decision["agents"]:
                decision["agents"].append("WEB_SEARCH")
                decision["rationale"] += " [Rule: Time-sensitive query, added WEB_SEARCH]"
        
        if any(keyword in query_lower for keyword in ["paper", "arxiv", "research", "study", "publication"]):
            if "ARXIV" not in decision["agents"]:
                decision["agents"].append("ARXIV")
                decision["rationale"] += " [Rule: Research query, added ARXIV]"
    
    def _fallback_routing(self, query, has_pdf_upload):
        query_lower = query.lower()
        agents = []
        rationale = "Fallback rule-based routing: "
        
        if has_pdf_upload:
            agents.append("PDF_RAG")
            rationale += "PDF uploaded; "
        
        if any(keyword in query_lower for keyword in ["paper", "arxiv", "research"]):
            agents.append("ARXIV")
            rationale += "Research-related query; "
        
        if any(keyword in query_lower for keyword in ["recent", "latest", "news", "today"]):
            agents.append("WEB_SEARCH")
            rationale += "Time-sensitive query; "
        
        if not agents:
            agents.append("WEB_SEARCH")
            rationale += "Default to web search"
        
        return {
            "agents": agents,
            "rationale": rationale,
            "priority": agents[0]
        }
    
    def get_logs(self):
        return self.decision_log
    
    def save_logs(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.decision_log, f, indent=2)
