import os
from dotenv import load_dotenv
from groq import Groq
from src.prompts import SYSTEM_PROMPT, REFUSAL_MESSAGE, is_refusal
from src.vector_store import search

load_dotenv()

def answer(user_query: str, chroma_path: str = None) -> str:
    if is_refusal(user_query):
        return REFUSAL_MESSAGE
    
    try:
        chunks = search(user_query, top_k=4)
        
        if not chunks:
            return "I could not find this information in my sources. Please check https://www.hdfcfund.com directly."
        
        context = ""
        for chunk in chunks:
            context += f"""---
Scheme: {chunk['scheme_name']}
Topic: {chunk['topic']}
Source: {chunk['source_url']}
Last Checked: {chunk['last_checked']}
Content: {chunk['text']}
---\n\n"""
        
        api_key = None
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY", None)
        except Exception:
            pass
        
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            return "Configuration error: GROQ_API_KEY not found."
        
        client = Groq(api_key=api_key)
        
        user_message = f"""Context from knowledge base:
{context}

Question: {user_query}

Formatting rules:
- Answer in 2-3 sentences max.
- End with source as a markdown hyperlink: [View Source](url)
- End with: Last updated from sources: [date]"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=512,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I could not process your request right now. Please try again later."
