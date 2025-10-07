import os
import google.generativeai as genai
import PyPDF2
from io import BytesIO

class PDFRAGAgent:
    def __init__(self, index_path="rag_index"):
        self.documents = []
        self.pdf_contents = {}
        
    def add_pdf(self, pdf_path):
        try:
            filename = os.path.basename(pdf_path)
            
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            
            # Store the content
            self.pdf_contents[filename] = text_content
            self.documents.append({"filename": filename, "path": pdf_path})
            
            return f"Successfully processed PDF: {filename} ({len(text_content)} characters extracted)"
            
        except Exception as e:
            return f"Error processing PDF {filename}: {str(e)}"
    
    def query(self, question):
        if not self.documents:
            return "No documents uploaded yet. Please upload a PDF first."
        
        try:
            # Get API key from environment
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return "Error: GEMINI_API_KEY not found in environment variables"
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Combine all PDF contents
            all_content = ""
            filenames = []
            for doc in self.documents:
                filename = doc["filename"]
                filenames.append(filename)
                if filename in self.pdf_contents:
                    all_content += f"\n\n=== Content from {filename} ===\n"
                    all_content += self.pdf_contents[filename]
            
            # Create prompt for AI
            prompt = f"""
Based on the following PDF documents: {', '.join(filenames)}

Document content:
{all_content[:8000]}

User question: {question}

Please provide a detailed answer based on the PDF content. If the information is not available in the documents, please say so clearly.
"""
            
            # Generate response
            response = model.generate_content(prompt)
            return f"Based on uploaded PDF(s) ({', '.join(filenames)}): {response.text}"
            
        except Exception as e:
            return f"Error querying documents: {str(e)}"
