import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from src.prompts import SYSTEM_PROMPT, REFUSAL_MESSAGE, is_refusal

# Load environment variables at the top
load_dotenv()

def load_retriever(chroma_path: str):
    import os
    if not os.path.isabs(chroma_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chroma_path = os.path.join(base_dir, "data", "chroma_db")
    """
    Loads the persistent ChromaDB collection "hdfc_mf_faq" 
    from chroma_path.
    Returns the collection object.
    If collection does not exist or is empty, raises a clear 
    RuntimeError with message:
    "Vector DB not found. Please run src/ingest.py first."
    """
    try:
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path=chroma_path)
        
        # Get the collection
        collection = client.get_collection("hdfc_mf_faq")
        
        # Check if collection has any documents
        count = collection.count()
        if count == 0:
            raise RuntimeError("Vector DB not found. Please run src/ingest.py first.")
        
        print(f"Loaded retriever with {count} documents")
        return collection
        
    except chromadb.errors.CollectionNotFoundError:
        raise RuntimeError("Vector DB not found. Please run src/ingest.py first.")
    except Exception as e:
        raise RuntimeError(f"Error loading vector DB: {e}")

def retrieve_chunks(query: str, collection, top_k: int = 4) -> list[dict]:
    """
    Embeds the query using sentence-transformers "all-MiniLM-L6-v2"
    Queries the ChromaDB collection for top_k most similar chunks.
    Returns a list of dicts, each with:
      - "text": the chunk document text
      - "source_url": from metadata
      - "scheme_name": from metadata
      - "topic": from metadata
      - "last_checked": from metadata
    """
    # Initialize embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Embed the query
    query_embedding = model.encode([query]).tolist()
    
    # Query the collection
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    
    # Format results into list of dicts
    chunks = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            chunk_dict = {
                "text": doc,
                "source_url": metadata.get("source_url", ""),
                "scheme_name": metadata.get("scheme_name", ""),
                "topic": metadata.get("topic", ""),
                "last_checked": metadata.get("last_checked", "")
            }
            chunks.append(chunk_dict)
    
    return chunks

def build_context(chunks: list[dict]) -> str:
    """
    Takes retrieved chunks and formats them into a single context string.
    Format for each chunk:
    ---
    Scheme: {scheme_name}
    Topic: {topic}
    Source: {source_url}
    Last Checked: {last_checked}
    Content: {text}
    ---
    Returns the full combined string.
    """
    context_parts = []
    
    for chunk in chunks:
        formatted_chunk = f"""---
Scheme: {chunk['scheme_name']}
Topic: {chunk['topic']}
Source: {chunk['source_url']}
Last Checked: {chunk['last_checked']}
Content: {chunk['text']}
---"""
        context_parts.append(formatted_chunk)
    
    return "\n\n".join(context_parts)

def ask_llm(user_query: str, context: str) -> str:
    """
    Calls Groq API using the groq Python client with:
    - model: "llama3-8b-8192"
    - system: SYSTEM_PROMPT from src.prompts
    - user message: 
        "Context from knowledge base:\n{context}\n\nQuestion: {user_query}"
    
    Uses:
      max_tokens=512
      temperature=0 (for factual consistency)
    
    Loads GROQ_API_KEY from .env using python-dotenv.
    Returns the assistant's text response as a string.
    """
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY", None)
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "Configuration error: GROQ_API_KEY not found."
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Build the user message
        user_message = f"""Context from knowledge base:
{context}

Question: {user_query}

Formatting rules (follow exactly):
- Answer in 2-3 sentences max.
- End with source as a markdown hyperlink: [View Source](url)
- End with: Last updated from sources: [date]"""
        
        # Call the API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=512,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Return the response text
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "Sorry, I could not process your request right now. Please try again later."

def answer(user_query: str, chroma_path: str = None) -> str:
    if chroma_path is None:
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chroma_path = os.path.join(base_dir, "data", "chroma_db")
    """
    Main function that orchestrates the full RAG pipeline:
    1. Check is_refusal(user_query) from src.prompts
       If True: return REFUSAL_MESSAGE immediately
    2. load_retriever(chroma_path)
    3. retrieve_chunks(user_query, collection, top_k=4)
    4. If no chunks retrieved: return "I could not find 
       this information in my sources. Please check 
       https://www.hdfcfund.com directly."
    5. build_context(chunks)
    6. ask_llm(user_query, context)
    7. Return the LLM response string
    """
    # Step 1: Check for refusal triggers
    if is_refusal(user_query):
        return REFUSAL_MESSAGE
    
    try:
        # Step 2: Load retriever
        collection = load_retriever(chroma_path)
        
        # Step 3: Retrieve relevant chunks
        chunks = retrieve_chunks(user_query, collection, top_k=4)
        
        # Step 4: Check if any chunks were retrieved
        if not chunks:
            return "I could not find this information in my sources. Please check https://www.hdfcfund.com directly."
        
        # Step 5: Build context from chunks
        context = build_context(chunks)
        
        # Step 6: Ask LLM for answer
        response = ask_llm(user_query, context)
        
        # Step 7: Return the response
        return response
        
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        print(f"Unexpected error in answer function: {e}")
        return "Sorry, I could not process your request right now. Please try again later."
