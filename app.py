import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from agents.controller_agent import ControllerAgent
from agents.pdf_rag_agent import PDFRAGAgent
from agents.web_search_agent import WebSearchAgent
from agents.arxiv_agent import ArxivAgent
import google.generativeai as genai

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app, origins='*')

UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

controller = ControllerAgent()
pdf_rag = PDFRAGAgent()
web_search = WebSearchAgent()
arxiv_agent = ArxivAgent()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            result = pdf_rag.add_pdf(filepath)
            
            return jsonify({
                "success": True,
                "message": result,
                "filename": filename
            })
        
        return jsonify({"error": "Invalid file type. Only PDF files are allowed."}), 400
    
    except Exception as e:
        print(f"Upload error: {str(e)}")  # Log to console for debugging
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/ask', methods=['POST'])
def ask():
    print(f"Ask route called - request data: {request.json}")  # Debug log
    data = request.json
    query = data.get('query', '')
    print(f"Query received: {query}")  # Debug log
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    has_pdf = len(pdf_rag.documents) > 0
    
    decision = controller.analyze_query(query, has_pdf)
    
    agents_called = decision.get('agents', [])
    agent_responses = {}
    
    if 'PDF_RAG' in agents_called:
        try:
            rag_result = pdf_rag.query(query)
            agent_responses['PDF_RAG'] = rag_result
        except Exception as e:
            agent_responses['PDF_RAG'] = {"error": str(e)}
    
    if 'WEB_SEARCH' in agents_called:
        try:
            web_result = web_search.search(query)
            agent_responses['WEB_SEARCH'] = web_result
        except Exception as e:
            agent_responses['WEB_SEARCH'] = {"error": str(e)}
    
    if 'ARXIV' in agents_called:
        try:
            arxiv_result = arxiv_agent.search_papers(query)
            agent_responses['ARXIV'] = arxiv_result
        except Exception as e:
            agent_responses['ARXIV'] = {"error": str(e)}
    
    final_answer = synthesize_answer(query, agent_responses)
    
    response = {
        "query": query,
        "decision": decision,
        "agents_used": agents_called,
        "agent_responses": agent_responses,
        "final_answer": final_answer,
        "timestamp": datetime.now().isoformat()
    }
    
    log_request(response)
    
    return jsonify(response)

def synthesize_answer(query, agent_responses):
    if not agent_responses:
        return "No agents were able to process your query."
    
    context_parts = []
    
    for agent_name, response in agent_responses.items():
        if isinstance(response, dict) and 'error' in response:
            context_parts.append(f"{agent_name}: Error - {response['error']}")
        elif isinstance(response, str):
            # Response is a string directly from the agent
            context_parts.append(f"{agent_name}: {response}")
        elif isinstance(response, dict):
            # Response is a dictionary, try to extract meaningful content
            if agent_name == 'PDF_RAG':
                context_parts.append(f"PDF RAG: {response.get('answer', response)}")
            elif agent_name == 'WEB_SEARCH':
                context_parts.append(f"Web Search: {response.get('summary', response)}")
            elif agent_name == 'ARXIV':
                context_parts.append(f"ArXiv: {response.get('summary', response)}")
            else:
                context_parts.append(f"{agent_name}: {response}")
        else:
            context_parts.append(f"{agent_name}: {str(response)}")
    
    context = "\n\n".join(context_parts) 
    prompt = f"""You are synthesizing answers from multiple AI agents. Combine the following agent responses into a single, coherent answer to the user's question.

User Question: {query}

Agent Responses:
{context}

Synthesized Answer:"""
    
    try:
        # Use Google Generative AI to synthesize the final answer
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text or "Unable to synthesize answer."
    except Exception as e:
        return f"Error synthesizing answer: {str(e)}\n\nRaw responses:\n{context}"

def log_request(data):
    log_file = f"logs/requests_{datetime.now().strftime('%Y%m%d')}.json"
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(data)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Logging error: {e}")

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        controller_logs = controller.get_logs()
        
        log_files = [f for f in os.listdir('logs') if f.endswith('.json')]
        request_logs = []
        
        for log_file in sorted(log_files, reverse=True)[:5]:
            with open(os.path.join('logs', log_file), 'r') as f:
                request_logs.extend(json.load(f))
        
        return jsonify({
            "controller_logs": controller_logs,
            "request_logs": request_logs[-50:]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
