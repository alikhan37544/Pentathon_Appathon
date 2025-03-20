import argparse
import sys
import os
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.chat_models import ChatOllama
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Question: {question}

Answer the question using only the provided context above. If the context doesn't contain information about the topic, reply with "I don't have specific information about this topic in my knowledge base."
"""

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    response_text = query_rag(query_text)
    print(response_text)


def query_rag(query_text: str):
    # Check if database exists
    if not os.path.exists(CHROMA_PATH):
        return "Error: Database not found. Please make sure to populate the database first."
    
    try:
        # Prepare the DB.
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        
        # Print debug info
        print(f"Database contains {db._collection.count()} documents", file=sys.stderr)
        
        # Search the DB.
        results = db.similarity_search_with_score(query_text, k=5)
        
        if not results:
            return "No relevant documents found in the database. Please try a different query or make sure documents are properly indexed."

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        # Updated to use ChatOllama instead of Ollama
        model = ChatOllama(model="llama3.2")
        response = model.invoke(prompt)
        
        # Extract just the content from the response
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)

        sources = [doc.metadata.get("source", "Unknown").split('/')[-1] for doc, _score in results]
        return response_text
    
    except Exception as e:
        import traceback
        return f"Error querying database: {str(e)}\n{traceback.format_exc()}"


if __name__ == "__main__":
    main()