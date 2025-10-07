#!/usr/bin/env python3
"""
Script to upload PixelPrompter files to Hugging Face Spaces
"""
import os
from huggingface_hub import HfApi, upload_folder
import sys

def upload_to_hf_space():
    """Upload all files to Hugging Face Space"""
    
    # Initialize Hugging Face API
    api = HfApi()
    
    # Your space details
    repo_id = "punamchanne/multi-agent-ai-system"
    repo_type = "space"
    
    print("🚀 Starting upload to Hugging Face Space...")
    print(f"📁 Repository: {repo_id}")
    
    try:
        # Get token from environment or prompt user
        token = os.environ.get("HF_TOKEN")
        if not token:
            print("⚠️  HF_TOKEN not found in environment variables")
            print("🔗 Please get your token from: https://huggingface.co/settings/tokens")
            token = input("Enter your Hugging Face token: ").strip()
        
        # Files to upload
        files_to_upload = [
            "app_gradio.py",
            "requirements.txt", 
            "README.md",
            ".env.example"
        ]
        
        # Upload individual files
        for file_path in files_to_upload:
            if os.path.exists(file_path):
                print(f"📤 Uploading {file_path}...")
                api.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=file_path,
                    repo_id=repo_id,
                    repo_type=repo_type,
                    token=token
                )
                print(f"✅ {file_path} uploaded successfully")
            else:
                print(f"❌ {file_path} not found")
        
        # Upload folders
        folders_to_upload = ["agents", "frontend", "sample_pdfs"]
        
        for folder in folders_to_upload:
            if os.path.exists(folder):
                print(f"📁 Uploading {folder} folder...")
                api.upload_folder(
                    folder_path=folder,
                    path_in_repo=folder,
                    repo_id=repo_id,
                    repo_type=repo_type,
                    token=token
                )
                print(f"✅ {folder} folder uploaded successfully")
            else:
                print(f"❌ {folder} folder not found")
        
        # Upload additional files
        additional_files = ["generate_sample_pdfs.py", "ingest_sample_pdfs.py"]
        for file_path in additional_files:
            if os.path.exists(file_path):
                print(f"📤 Uploading {file_path}...")
                api.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=file_path,
                    repo_id=repo_id,
                    repo_type=repo_type,
                    token=token
                )
                print(f"✅ {file_path} uploaded successfully")
        
        print(f"\n🎉 Deployment completed successfully!")
        print(f"🌐 Your Space: https://huggingface.co/spaces/{repo_id}")
        print(f"⚙️  Don't forget to set GEMINI_API_KEY in Space settings!")
        
    except Exception as e:
        print(f"❌ Error during upload: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you have a valid Hugging Face token")
        print("2. Check that the repository exists and you have write access")
        print("3. Verify your internet connection")
        return False
    
    return True

if __name__ == "__main__":
    success = upload_to_hf_space()
    sys.exit(0 if success else 1)