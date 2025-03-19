#!/bin/bash
# filepath: /home/atom/Coding/Projects/Pentathon_Appathon/new_frontend/reset_and_setup.sh

echo "Resetting database and setting up environment..."

# Reset database directories
rm -rf chroma
mkdir -p chroma
mkdir -p data

# Reset import issue by making sure files are properly located
echo "Checking for embedding function file..."
if [ -f "get_embedding_function.py" ]; then
  echo "Embedding function module exists"
else
  echo "Creating embedding function module..."
  cat > get_embedding_function.py << 'EOF'
from langchain_community.embeddings.ollama import OllamaEmbeddings

def get_embedding_function():
    embeddings = OllamaEmbeddings(model="llama3.2")
    return embeddings
EOF
fi

echo "Setup complete! Now you can:"
echo "1. Upload your PDF documents using the web interface"
echo "2. Populate the database using the 'Populate Database' button"
echo "3. Query your documents"