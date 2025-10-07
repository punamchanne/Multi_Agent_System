import gradio as gr
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import json
import tempfile
import shutil

# Load environment variables
load_dotenv()

# Import your agents
try:
    from agents.controller_agent import ControllerAgent
    from agents.pdf_rag_agent import PDFRAGAgent
    from agents.web_search_agent import WebSearchAgent
    from agents.arxiv_agent import ArxivAgent
except ImportError as e:
    print(f"Warning: Could not import agents: {e}")
    # Create dummy classes for testing
    class DummyAgent:
        def __init__(self): pass
        def analyze_query(self, query, has_pdf): return {"agents": ["web"]}
        def query(self, query): return f"PDF response for: {query}"
        def search(self, query): return f"Web search response for: {query}"
        def search_papers(self, query): return f"ArXiv response for: {query}"
        def add_pdf(self, path): return True
        @property
        def documents(self): return []
    
    ControllerAgent = PDFRAGAgent = WebSearchAgent = ArxivAgent = DummyAgent

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️ Warning: GEMINI_API_KEY not found in environment variables")

# Initialize agents
controller = ControllerAgent()
pdf_rag = PDFRAGAgent()
web_search = WebSearchAgent()
arxiv_agent = ArxivAgent()

# Create directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('sample_pdfs', exist_ok=True)

def process_pdf_upload(pdf_file):
    """Handle PDF file upload"""
    if pdf_file is None:
        return "❌ No file uploaded"
    
    try:
        # Get the file path
        filename = os.path.basename(pdf_file.name)
        
        # Copy file to uploads directory
        upload_path = os.path.join('uploads', filename)
        shutil.copy2(pdf_file.name, upload_path)
        
        # Process with PDF agent
        pdf_rag.add_pdf(upload_path)
        return f"✅ Successfully uploaded and processed: {filename}"
    
    except Exception as e:
        return f"❌ Error uploading file: {str(e)}"

def ask_question(question, chat_history):
    """Process user question and return response"""
    if not question.strip():
        return chat_history, ""
    
    print(f"🔍 Processing question: {question}")
    
    try:
        # Check if PDFs are available
        has_pdf = len(getattr(pdf_rag, 'documents', [])) > 0
        
        # Use controller to determine which agents to use
        agent_decision = controller.analyze_query(question, has_pdf)
        
        agent_responses = {}
        agents_used = []
        
        # Call appropriate agents based on decision
        if 'pdf' in agent_decision.get('agents', []) and has_pdf:
            try:
                pdf_response = pdf_rag.query(question)
                if pdf_response:
                    agent_responses['PDF Agent'] = pdf_response
                    agents_used.append('PDF Agent')
            except Exception as e:
                agent_responses['PDF Agent'] = f"Error: {str(e)}"
        
        if 'web' in agent_decision.get('agents', []):
            try:
                web_response = web_search.search(question)
                if web_response:
                    agent_responses['Web Search Agent'] = web_response
                    agents_used.append('Web Search Agent')
            except Exception as e:
                agent_responses['Web Search Agent'] = f"Error: {str(e)}"
        
        if 'arxiv' in agent_decision.get('agents', []):
            try:
                arxiv_response = arxiv_agent.search_papers(question)
                if arxiv_response:
                    agent_responses['ArXiv Agent'] = arxiv_response
                    agents_used.append('ArXiv Agent')
            except Exception as e:
                agent_responses['ArXiv Agent'] = f"Error: {str(e)}"
        
        # If no agents were called, default to web search
        if not agent_responses:
            try:
                web_response = web_search.search(question)
                agent_responses['Web Search Agent'] = web_response or "No results found"
                agents_used.append('Web Search Agent')
            except Exception as e:
                agent_responses['Web Search Agent'] = f"Error: {str(e)}"
        
        # Synthesize final answer
        final_answer = synthesize_answer(question, agent_responses)
        
        # Format response with agent attribution
        response_text = f"**Agents Used:** {', '.join(agents_used)}\n\n"
        response_text += f"**Answer:** {final_answer}"
        
        # Update chat history
        chat_history.append([question, response_text])
        
        return chat_history, ""
    
    except Exception as e:
        error_response = f"❌ Error processing question: {str(e)}"
        chat_history.append([question, error_response])
        return chat_history, ""

def synthesize_answer(query, agent_responses):
    """Combine responses from multiple agents"""
    if not agent_responses:
        return "I couldn't find any relevant information for your question."
    
    if len(agent_responses) == 1:
        return list(agent_responses.values())[0]
    
    # Try to use Gemini for synthesis if available
    if api_key:
        try:
            context_parts = []
            for agent_name, response in agent_responses.items():
                context_parts.append(f"From {agent_name}: {response}")
            
            context = "\n\n".join(context_parts)
            
            prompt = f"""You are synthesizing answers from multiple AI agents. Combine the following agent responses into a single, coherent answer.

User Question: {query}

Agent Responses:
{context}

Please provide a well-structured, comprehensive answer that integrates the information from all agents.

Synthesized Answer:"""
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"Error with Gemini synthesis: {e}")
    
    # Fallback: simple combination
    combined_parts = []
    for agent_name, response in agent_responses.items():
        combined_parts.append(f"**From {agent_name}:**\n{response}")
    
    return "\n\n".join(combined_parts)

def clear_chat():
    """Clear chat history"""
    return []

def get_sample_pdfs():
    """Get list of sample PDFs"""
    sample_dir = 'sample_pdfs'
    if os.path.exists(sample_dir):
        return [f for f in os.listdir(sample_dir) if f.endswith('.pdf')]
    return []

def load_sample_pdf(pdf_name):
    """Load a sample PDF"""
    if not pdf_name:
        return "Please select a sample PDF"
    
    try:
        sample_path = os.path.join('sample_pdfs', pdf_name)
        if os.path.exists(sample_path):
            pdf_rag.add_pdf(sample_path)
            return f"✅ Loaded sample PDF: {pdf_name}"
        else:
            return f"❌ Sample PDF not found: {pdf_name}"
    except Exception as e:
        return f"❌ Error loading sample PDF: {str(e)}"

def generate_sample_pdfs():
    """Generate sample PDFs if they don't exist"""
    try:
        if os.path.exists('generate_sample_pdfs.py'):
            exec(open('generate_sample_pdfs.py').read())
            return "✅ Sample PDFs generated successfully"
        else:
            return "⚠️ Sample PDF generator not found"
    except Exception as e:
        return f"❌ Error generating sample PDFs: {str(e)}"

# Custom CSS for better styling
css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.main-header {
    text-align: center;
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.upload-section {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}
"""

# Create Gradio interface
with gr.Blocks(title="PixelPrompter - Multi-Agent AI System", css=css) as demo:
    gr.HTML("""
    <div class="main-header">
        <h1>🤖 PixelPrompter - Multi-Agent AI System</h1>
        <p>Intelligent AI system using specialized agents working together</p>
    </div>
    """)
    
    gr.Markdown("""
    **How it works:**
    - **PDF Agent**: Answers questions from your uploaded documents
    - **Web Search Agent**: Finds latest information from the internet  
    - **ArXiv Agent**: Searches academic papers and research
    - **Controller Agent**: Decides which agents to use for each question
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### 📄 Upload Documents")
                
                # File upload
                pdf_upload = gr.File(
                    label="Upload PDF File",
                    file_types=[".pdf"],
                    file_count="single"
                )
                upload_status = gr.Textbox(
                    label="Upload Status",
                    interactive=False
                )
                upload_btn = gr.Button("Upload PDF", variant="primary")
            
            with gr.Group():
                gr.Markdown("### 📚 Sample PDFs")
                sample_dropdown = gr.Dropdown(
                    choices=get_sample_pdfs(),
                    label="Select Sample PDF",
                    value=None
                )
                sample_status = gr.Textbox(
                    label="Sample PDF Status",
                    interactive=False
                )
                sample_btn = gr.Button("Load Sample PDF")
                generate_btn = gr.Button("Generate Sample PDFs", variant="secondary")
            
            with gr.Group():
                gr.Markdown("### 🛠️ Controls")
                clear_btn = gr.Button("Clear Chat", variant="secondary")
        
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat with PixelPrompter")
            
            # Chat interface
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                show_label=False,
                type="messages"
            )
            
            with gr.Row():
                question_input = gr.Textbox(
                    label="Ask a question",
                    placeholder="Ask about your PDFs, current events, or research papers...",
                    lines=2,
                    scale=4
                )
                ask_btn = gr.Button("Ask Question", variant="primary", scale=1)
    
    # Example questions
    gr.Markdown("""
    ### 💡 Example Questions to Try:
    - **PDF Questions**: "What is machine learning according to my document?"
    - **Current Events**: "Latest developments in AI this week"
    - **Research**: "Recent papers on transformer architectures"
    - **Combined**: "Explain RAG systems from my PDF and find related research"
    """)
    
    # Event handlers
    upload_btn.click(
        fn=process_pdf_upload,
        inputs=[pdf_upload],
        outputs=[upload_status]
    )
    
    sample_btn.click(
        fn=load_sample_pdf,
        inputs=[sample_dropdown],
        outputs=[sample_status]
    )
    
    generate_btn.click(
        fn=generate_sample_pdfs,
        outputs=[sample_status]
    )
    
    ask_btn.click(
        fn=ask_question,
        inputs=[question_input, chatbot],
        outputs=[chatbot, question_input]
    )
    
    question_input.submit(
        fn=ask_question,
        inputs=[question_input, chatbot],
        outputs=[chatbot, question_input]
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot]
    )

# Generate sample PDFs on startup
if __name__ == "__main__":
    print("🚀 Starting PixelPrompter...")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🔑 API key configured: {'Yes' if api_key else 'No'}")
    
    # Try to generate sample PDFs
    try:
        if os.path.exists('generate_sample_pdfs.py'):
            exec(open('generate_sample_pdfs.py').read())
            print("✅ Sample PDFs generated successfully")
        else:
            print("⚠️ generate_sample_pdfs.py not found")
    except Exception as e:
        print(f"⚠️ Warning: Could not generate sample PDFs: {e}")
    
    # Test agent imports
    try:
        print("🧪 Testing agent functionality...")
        decision = controller.analyze_query("test", False)
        print(f"✅ Controller working: {decision.get('agents', [])}")
    except Exception as e:
        print(f"⚠️ Controller test failed: {e}")
    
    # Launch the interface
    print("🌐 Launching Gradio interface...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )