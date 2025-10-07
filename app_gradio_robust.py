import gradio as gr
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    print("✅ Gemini API configured")
else:
    print("⚠️ Warning: GEMINI_API_KEY not found")

# Simple fallback implementations for when agents fail
class SimpleAgents:
    @staticmethod
    def web_search(query):
        """Simple web search fallback"""
        return f"Web search results for '{query}': This is a demo response. In a real deployment, this would search the web using DuckDuckGo and return actual results."
    
    @staticmethod  
    def arxiv_search(query):
        """Simple arxiv search fallback"""
        return f"ArXiv search results for '{query}': This is a demo response. In a real deployment, this would search ArXiv for academic papers related to your query."
    
    @staticmethod
    def pdf_query(query):
        """Simple PDF query fallback"""
        return f"PDF query response for '{query}': No PDFs have been uploaded yet. Please upload a PDF document to search through it."

# Try to import real agents, fall back to simple ones if they fail
try:
    from agents.controller_agent import ControllerAgent
    from agents.pdf_rag_agent import PDFRAGAgent
    from agents.web_search_agent import WebSearchAgent
    from agents.arxiv_agent import ArxivAgent
    
    controller = ControllerAgent()
    pdf_rag = PDFRAGAgent()
    web_search = WebSearchAgent()
    arxiv_agent = ArxivAgent()
    
    agents_loaded = True
    print("✅ All agents loaded successfully")
    
except Exception as e:
    print(f"⚠️ Warning: Could not load agents ({e}), using fallbacks")
    agents_loaded = False

def process_question(question, chat_history):
    """Process user question with robust error handling"""
    if not question.strip():
        return chat_history, ""
    
    try:
        if agents_loaded:
            # Use real agents
            has_pdf = len(getattr(pdf_rag, 'documents', [])) > 0
            
            # Get agent decision
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
                except:
                    responses.append(f"**Fallback:** {SimpleAgents.web_search(question)}")
            
            final_response = "\n\n".join(responses)
            agents_info = f"**Agents Used:** {', '.join(agents_used)}\n\n" if agents_used else ""
            final_answer = agents_info + final_response
            
        else:
            # Use fallback agents
            if "pdf" in question.lower() or "document" in question.lower():
                final_answer = SimpleAgents.pdf_query(question)
            elif "paper" in question.lower() or "research" in question.lower():
                final_answer = SimpleAgents.arxiv_search(question)
            else:
                final_answer = SimpleAgents.web_search(question)
        
        # Update chat history
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": final_answer})
        
        return chat_history, ""
        
    except Exception as e:
        error_message = f"❌ Error processing question: {str(e)}"
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": error_message})
        return chat_history, ""

def upload_pdf(pdf_file):
    """Handle PDF upload with robust error handling"""
    if pdf_file is None:
        return "❌ No file uploaded"
    
    try:
        if agents_loaded and hasattr(pdf_rag, 'add_pdf'):
            # Use real PDF agent
            filename = os.path.basename(pdf_file.name)
            upload_path = os.path.join('uploads', filename)
            
            # Ensure uploads directory exists
            os.makedirs('uploads', exist_ok=True)
            
            # Copy file
            import shutil
            shutil.copy2(pdf_file.name, upload_path)
            
            # Process with PDF agent
            pdf_rag.add_pdf(upload_path)
            return f"✅ Successfully uploaded and processed: {filename}"
        else:
            return "⚠️ PDF processing not available in demo mode"
            
    except Exception as e:
        return f"❌ Error uploading file: {str(e)}"

def clear_chat():
    """Clear chat history"""
    return []

# Create the Gradio interface
with gr.Blocks(title="PixelPrompter - Multi-Agent AI System") as demo:
    gr.HTML("""
    <div style="text-align: center; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
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
                gr.Markdown("### 🛠️ Controls")
                clear_btn = gr.Button("Clear Chat", variant="secondary")
        
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat with PixelPrompter")
            
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                show_label=False,
                type="messages"
            )
            
            with gr.Row():
                question_input = gr.Textbox(
                    label="Ask a question",
                    placeholder="Ask about PDFs, current events, or research papers...",
                    lines=2,
                    scale=4
                )
                ask_btn = gr.Button("Ask Question", variant="primary", scale=1)
    
    gr.Markdown("""
    ### 💡 Example Questions:
    - **PDF Questions**: "What is machine learning according to my document?"
    - **Current Events**: "Latest developments in AI this week"
    - **Research**: "Recent papers on transformer architectures"
    - **Combined**: "Explain RAG systems from my PDF and find related research"
    """)
    
    # Event handlers
    upload_btn.click(
        fn=upload_pdf,
        inputs=[pdf_upload],
        outputs=[upload_status]
    )
    
    ask_btn.click(
        fn=process_question,
        inputs=[question_input, chatbot],
        outputs=[chatbot, question_input]
    )
    
    question_input.submit(
        fn=process_question,
        inputs=[question_input, chatbot],
        outputs=[chatbot, question_input]
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot]
    )

# Launch the app
if __name__ == "__main__":
    print("🚀 Starting PixelPrompter (Robust Version)...")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🔑 API key configured: {'Yes' if api_key else 'No'}")
    print(f"🤖 Agents loaded: {'Yes' if agents_loaded else 'No (using fallbacks)'}")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )