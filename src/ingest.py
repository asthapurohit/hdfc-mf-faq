import csv
import time
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings

def load_sources(csv_path: str) -> list[dict]:
    """
    Reads data/sources.csv
    Returns list of dicts with keys: id, scheme_name, topic, url, last_checked
    """
    sources = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                sources.append(row)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return sources

def scrape_url(url: str) -> str:
    """
    Fetches a URL using requests with a 10 second timeout.
    Parses with BeautifulSoup, extracts only visible text (no scripts, no styles).
    Returns plain text string.
    If fetch fails, prints a warning and returns empty string. Never raises.
    """
    # Skip PDFs
    if url.lower().endswith('.pdf'):
        print(f"Skipping PDF: {url}")
        return ""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get visible text
        text = soup.get_text(separator=' ', strip=True)
        return text
        
    except requests.RequestException as e:
        print(f"Warning: Failed to fetch {url}: {e}")
        return ""
    except Exception as e:
        print(f"Warning: Error processing {url}: {e}")
        return ""

def chunk_text(text: str, source_meta: dict) -> list[dict]:
    """
    Splits text using LangChain's RecursiveCharacterTextSplitter:
      chunk_size=500, chunk_overlap=50
    For each chunk, returns a dict with:
      - "text": the chunk content
      - "source_url": source_meta["url"]
      - "scheme_name": source_meta["scheme_name"]
      - "topic": source_meta["topic"]
      - "last_checked": source_meta["last_checked"]
    Returns list of these dicts.
    """
    if not text.strip():
        return []
    
    # Initialize text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Split text into chunks
    chunks = splitter.split_text(text)
    
    # Create chunk dictionaries with metadata
    chunk_dicts = []
    for chunk in chunks:
        chunk_dict = {
            "text": chunk,
            "source_url": source_meta["url"],
            "scheme_name": source_meta["scheme_name"],
            "topic": source_meta["topic"],
            "last_checked": source_meta["last_checked"]
        }
        chunk_dicts.append(chunk_dict)
    
    return chunk_dicts

def embed_and_store(chunks: list[dict], chroma_path: str):
    if not chunks:
        print("No chunks to store")
        return
    
    client = chromadb.PersistentClient(path=chroma_path)
    
    try:
        client.delete_collection("hdfc_mf_faq")
        print("Cleared existing collection")
    except:
        pass
    
    collection = client.create_collection(
        name="hdfc_mf_faq",
        embedding_function=chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
    )
    
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "source_url": chunk["source_url"],
            "scheme_name": chunk["scheme_name"],
            "topic": chunk["topic"],
            "last_checked": chunk["last_checked"]
        }
        for chunk in chunks
    ]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB")

def ingest_knowledge_base(chroma_path: str):
    from src.knowledge_base import KNOWLEDGE_BASE
    
    client = chromadb.PersistentClient(path=chroma_path)
    
    try:
        client.delete_collection("hdfc_mf_faq")
        print("Cleared existing collection")
    except:
        pass
    
    collection = client.create_collection(
        name="hdfc_mf_faq",
        embedding_function=chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
    )
    
    texts = [item["text"] for item in KNOWLEDGE_BASE]
    metadatas = [
        {
            "source_url": item["source_url"],
            "scheme_name": item["scheme_name"],
            "topic": item["topic"],
            "last_checked": item["last_checked"]
        }
        for item in KNOWLEDGE_BASE
    ]
    ids = [f"kb_{i}" for i in range(len(KNOWLEDGE_BASE))]
    
    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Ingested {len(KNOWLEDGE_BASE)} knowledge base entries")

def main():
    """
    Calls load_sources → scrape_url → chunk_text → embed_and_store
    Prints: "Ingestion complete. Total chunks stored: X"
    """
    print("Starting ingestion pipeline...")
    
    # Load sources from CSV
    sources = load_sources("data/sources.csv")
    print(f"Loaded {len(sources)} sources")
    
    if not sources:
        print("No sources found. Exiting.")
        return
    
    all_chunks = []
    
    # Process each source
    for i, source in enumerate(sources):
        print(f"\nProcessing source {i+1}/{len(sources)}: {source['scheme_name']} - {source['topic']}")
        
        # Scrape URL
        text = scrape_url(source["url"])
        
        if text:
            # Chunk text
            chunks = chunk_text(text, source)
            all_chunks.extend(chunks)
            print(f"Generated {len(chunks)} chunks from {source['url']}")
        else:
            print(f"No content retrieved from {source['url']}")
        
        # Sleep between requests to be respectful
        if i < len(sources) - 1:
            time.sleep(1)
    
    # Store chunks in ChromaDB
    if all_chunks:
        embed_and_store(all_chunks, "data/chroma_db")
        print(f"\nIngestion complete. Total chunks stored: {len(all_chunks)}")
    else:
        print("\nNo chunks to store. Ingestion failed.")

if __name__ == "__main__":
    main()
