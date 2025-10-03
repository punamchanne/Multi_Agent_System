import os
import pickle
import fitz
import numpy as np
import faiss
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class PDFRAGAgent:
    def __init__(self, index_path="rag_index"):
        self.index_path = index_path
        self.documents = []
        self.index = None
        self.dimension = 768
        
        if os.path.exists(f"{index_path}.faiss") and os.path.exists(f"{index_path}.pkl"):
            self.load_index()
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num, page in enumerate(doc):
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def chunk_text(self, text, chunk_size=500, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def get_embedding(self, text):
        try:
            response = client.models.embed_content(
                model="models/text-embedding-004",
                contents=text
            )
            embedding = response.embeddings[0].values
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            print(f"Embedding error: {e}")
            return np.random.rand(self.dimension).astype(np.float32)
    
    def ingest_pdf(self, pdf_path, metadata=None):
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text)
        
        doc_name = os.path.basename(pdf_path)
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        for idx, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk)
            
            self.index.add(np.array([embedding]))
            
            doc_entry = {
                "id": len(self.documents),
                "source": doc_name,
                "chunk_id": idx,
                "text": chunk,
                "metadata": metadata or {}
            }
            self.documents.append(doc_entry)
        
        self.save_index()
        return f"Ingested {len(chunks)} chunks from {doc_name}"
    
    def retrieve(self, query, top_k=3):
        if self.index is None or self.index.ntotal == 0:
            return []
        
        query_embedding = self.get_embedding(query)
        
        distances, indices = self.index.search(np.array([query_embedding]), top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["distance"] = float(distance)
                results.append(doc)
        
        return results
    
    def query(self, user_query, top_k=3):
        if self.index is None or self.index.ntotal == 0:
            return {
                "answer": "No documents in the RAG system. Please upload PDFs first.",
                "sources": [],
                "retrieved_docs": []
            }
        
        retrieved_docs = self.retrieve(user_query, top_k)
        
        context = "\n\n".join([f"[Source: {doc['source']}]\n{doc['text']}" for doc in retrieved_docs])
        
        prompt = f"""Based on the following document excerpts, answer the user's question.
If the information is not in the documents, say so.

Documents:
{context}

Question: {user_query}

Answer:"""
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            answer = response.text
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"
        
        return {
            "answer": answer,
            "sources": list(set([doc["source"] for doc in retrieved_docs])),
            "retrieved_docs": retrieved_docs
        }
    
    def save_index(self):
        faiss.write_index(self.index, f"{self.index_path}.faiss")
        with open(f"{self.index_path}.pkl", "wb") as f:
            pickle.dump(self.documents, f)
    
    def load_index(self):
        self.index = faiss.read_index(f"{self.index_path}.faiss")
        with open(f"{self.index_path}.pkl", "rb") as f:
            self.documents = pickle.load(f)
