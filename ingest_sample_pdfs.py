import os
from agents.pdf_rag_agent import PDFRAGAgent

rag_agent = PDFRAGAgent()

sample_pdfs_dir = 'sample_pdfs'

if not os.path.exists(sample_pdfs_dir):
    print(f"Error: {sample_pdfs_dir} directory not found.")
    print("Please run generate_sample_pdfs.py first.")
    exit(1)

pdf_files = [f for f in os.listdir(sample_pdfs_dir) if f.endswith('.pdf')]

if not pdf_files:
    print(f"No PDF files found in {sample_pdfs_dir}")
    exit(1)

print(f"Found {len(pdf_files)} PDF files. Starting ingestion...\n")

for pdf_file in pdf_files:
    pdf_path = os.path.join(sample_pdfs_dir, pdf_file)
    print(f"Ingesting: {pdf_file}")
    
    try:
        result = rag_agent.ingest_pdf(pdf_path, metadata={"category": "NebulaByte"})
        print(f"  ✓ {result}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    print()

print("Ingestion complete!")
print(f"Total documents in index: {rag_agent.index.ntotal if rag_agent.index else 0}")
