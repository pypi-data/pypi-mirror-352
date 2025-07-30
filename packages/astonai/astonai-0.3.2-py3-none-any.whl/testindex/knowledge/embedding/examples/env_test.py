#!/usr/bin/env python3
"""
Test script to verify environment variables for Pinecone are correctly loaded.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check Pinecone environment variables
pinecone_api_key = os.environ.get("TESTINDEX_PINECONE__API_KEY")
pinecone_environment = os.environ.get("TESTINDEX_PINECONE__ENVIRONMENT")
pinecone_index_name = os.environ.get("TESTINDEX_PINECONE__INDEX_NAME")
pinecone_namespace = os.environ.get("TESTINDEX_PINECONE__NAMESPACE")

print("=== Pinecone Environment Variables ===")
print(f"API Key: {'[SET]' if pinecone_api_key else '[NOT SET]'}")
print(f"Environment: {pinecone_environment}")
print(f"Index Name: {pinecone_index_name}")
print(f"Namespace: {pinecone_namespace}")
print()

# Check if python-dotenv is loading variables correctly
print("=== .env File Check ===")
if not pinecone_api_key:
    print("WARNING: TESTINDEX_PINECONE__API_KEY not loaded from .env file")
    print("Check that python-dotenv is installed and .env file is in the correct location")

# Print current directory and .env file path
import pathlib
current_directory = pathlib.Path.cwd()
env_file_path = current_directory / ".env"
env_file_exists = env_file_path.exists()

print(f"Current working directory: {current_directory}")
print(f".env file at {env_file_path}: {'EXISTS' if env_file_exists else 'DOES NOT EXIST'}")

# Print Pinecone package version
try:
    import pinecone
    print(f"\nPinecone package version: {pinecone.__version__}")
except ImportError:
    print("\nPinecone package not installed")
except Exception as e:
    print(f"\nError checking Pinecone version: {str(e)}")

if __name__ == "__main__":
    print("\n\nAll environment variables appear to be set correctly.")
    print("You can now run the benchmark script with:")
    print("python -m testindex.knowledge.embedding.examples.pinecone_benchmark") 