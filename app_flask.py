import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import agents with error handling for HF deployment
try:
    from agents.controller_agent import ControllerAgent
    from agents.pdf_rag_agent import PDFRAGAgent
    from agents.web_search_agent import WebSearchAgent
    from agents.arxiv_agent import ArxivAgent
    import google.generativeai as genai
    
    # Configure Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured")
    else:
        print("⚠️ Warning: GEMINI_API_KEY not found")
    
    # Initialize agents
    controller = ControllerAgent()
    pdf_rag = PDFRAGAgent()
    web_search = WebSearchAgent()
    arxiv_agent = ArxivAgent()
    
    agents_loaded = True
    print("✅ All agents loaded successfully")
    
except Exception as e:
    print(f"⚠️ Warning: Could not load agents ({e}), using fallbacks")
    
    # Fallback implementations
    class FallbackAgent:
        def analyze_query(self, query, has_pdf=False):
            return {"agents": ["web"]}
        
        def query(self, query):
            return f"Fallback response for: {query}"
        
        def search(self, query):
            return f"Fallback search for: {query}"
        
        def search_papers(self, query):
            return f"Fallback research for: {query}"
        
        def add_pdf(self, path):
            return "PDF processing not available in fallback mode"
        
        def get_logs(self):
            return []
    
    controller = FallbackAgent()
    pdf_rag = FallbackAgent()
    web_search = FallbackAgent()
    arxiv_agent = FallbackAgent()
    
    agents_loaded = False

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Configure CORS for both local and HF deployment
CORS(app, origins=['*'])  # Allow all origins for HF compatibility

UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

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
            
            if agents_loaded:
                pdf_rag.add_pdf(filepath)
            
            return jsonify({
                "message": f"File {filename} uploaded successfully!",
                "filename": filename,
                "agents_status": "active" if agents_loaded else "fallback"
            })
        
        return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "No question provided"}), 400
        
        question = data['question']
        
        # Log the request
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "method": "ask"
        }
        
        if agents_loaded:
            # Check if PDFs are available
            has_pdf = len(getattr(pdf_rag, 'documents', [])) > 0
            
            # Get routing decision
            decision = controller.analyze_query(question, has_pdf)
            agents_to_use = decision.get('agents', ['web'])
            
            responses = []
            agents_used = []
            
            # Call appropriate agents
            for agent_name in agents_to_use:
                try:
                    if agent_name.lower() in ['web', 'web_search'] or 'web' in agent_name.lower():
                        response = web_search.search(question)
                        responses.append(f"**Web Search:** {response}")
                        agents_used.append("Web Search")
                        
                    elif agent_name.lower() in ['arxiv', 'research'] or 'arxiv' in agent_name.lower():
                        response = arxiv_agent.search_papers(question)
                        responses.append(f"**ArXiv Research:** {response}")
                        agents_used.append("ArXiv")
                        
                    elif agent_name.lower() in ['pdf', 'rag'] or 'pdf' in agent_name.lower():
                        if has_pdf:
                            response = pdf_rag.query(question)
                            responses.append(f"**PDF Documents:** {response}")
                            agents_used.append("PDF RAG")
                        else:
                            responses.append("**PDF Documents:** No PDFs uploaded yet.")
                            
                except Exception as e:
                    responses.append(f"**Error with {agent_name}:** {str(e)}")
            
            if not responses:
                # Default to web search
                try:
                    response = web_search.search(question)
                    responses.append(f"**Web Search:** {response}")
                    agents_used.append("Web Search")
                except Exception as e:
                    responses.append(f"**Fallback:** Could not process query: {str(e)}")
            
            final_response = "\n\n".join(responses)
            agents_info = f"**Agents Used:** {', '.join(agents_used)}\n\n" if agents_used else ""
            answer = agents_info + final_response
            
        else:
            # Fallback response
            answer = f"**Fallback Mode:** Your question '{question}' has been received. Agents are not fully loaded, but the system is operational."
        
        log_entry["answer"] = answer
        log_entry["agents_used"] = agents_used if agents_loaded else ["fallback"]
        
        # Save log
        log_file = f"logs/requests_{datetime.now().strftime('%Y%m%d')}.json"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return jsonify({
            "answer": answer,
            "agents_used": agents_used if agents_loaded else ["fallback"],
            "agents_status": "active" if agents_loaded else "fallback"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs')
def get_logs():
    try:
        if agents_loaded:
            controller_logs = controller.get_logs()
        else:
            controller_logs = []
        
        log_files = [f for f in os.listdir('logs') if f.endswith('.json')]
        request_logs = []
        
        for log_file in sorted(log_files, reverse=True)[:5]:
            try:
                with open(os.path.join('logs', log_file), 'r') as f:
                    request_logs.extend(json.load(f))
            except:
                continue
        
        return jsonify({
            "controller_logs": controller_logs,
            "request_logs": request_logs[-50:],
            "agents_status": "active" if agents_loaded else "fallback"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "agents_loaded": agents_loaded,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Multi-Agent AI System (Flask + HTML Interface)...")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🔑 API key configured: {'Yes' if os.environ.get('GEMINI_API_KEY') else 'No'}")
    print(f"🤖 Agents loaded: {'Yes' if agents_loaded else 'No (using fallbacks)'}")
    
    # Get port from environment (for HF compatibility) or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=True
    )