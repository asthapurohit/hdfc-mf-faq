import streamlit as st
from src.rag import answer
from src.prompts import DISCLAIMER

st.set_page_config(
    page_title="HDFC MF FAQ Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { box-sizing: border-box; font-family: 'Inter', sans-serif; }

header[data-testid="stHeader"] { display: none; }
#MainMenu { display: none; }
footer { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stAppViewContainer"] { padding: 0 !important; }
div[data-testid="stAppViewBlockContainer"] { padding: 0 !important; }

.top-nav {
    background: white;
    border-bottom: 2.5px solid #00D09C;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.nav-logo {
    font-size: 15px;
    font-weight: 700;
    color: #004C8F;
    display: flex;
    align-items: center;
    gap: 8px;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 8px;
}
.npill {
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
}
.npill-groww {
    background: #e6faf5;
    color: #007a5a;
    border: 1px solid #00D09C;
    text-decoration: none;
}
.npill-hdfc {
    background: #fef0f0;
    color: #c0131a;
    border: 1px solid #ED232A;
}
.npill-rag {
    background: #e8f0fe;
    color: #1a56db;
    border: 1px solid #c5d8fd;
}
.npill-facts {
    background: #e6faf5;
    color: #007a5a;
    border: 1px solid #00D09C;
}

.stats-bar {
    background: #004C8F;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.stats-left { display: flex; gap: 32px; }
.stat-num { font-size: 20px; font-weight: 700; color: #00D09C; }
.stat-lbl { font-size: 10px; color: #a0b8d4; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 1px; }
.stats-right { font-size: 11px; color: #a0b8d4; display: flex; align-items: center; gap: 6px; }
.live-dot { width: 7px; height: 7px; border-radius: 50%; background: #00D09C; display: inline-block; }

.scheme-strip {
    background: white;
    border-bottom: 1px solid #e8eaf0;
    padding: 10px 24px;
    display: flex;
    gap: 8px;
    align-items: center;
    overflow-x: auto;
}
.strip-label { font-size: 11px; color: #888; font-weight: 600; white-space: nowrap; margin-right: 6px; text-transform: uppercase; letter-spacing: 0.06em; }
.scheme-chip {
    display: flex;
    flex-direction: column;
    background: #f8f9ff;
    border: 1px solid #e8eaf0;
    border-radius: 8px;
    padding: 6px 12px;
    white-space: nowrap;
    min-width: 130px;
}
.chip-cat { font-size: 9px; font-weight: 700; color: #00897b; text-transform: uppercase; letter-spacing: 0.06em; }
.chip-name { font-size: 11px; font-weight: 600; color: #1a1a2e; margin-top: 2px; }

.main-layout {
    display: flex;
    height: calc(100vh - 160px);
    background: #f4faf8;
}

.chat-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
    border-right: 1px solid #e8eaf0;
}
.chat-top-bar {
    padding: 12px 16px;
    border-bottom: 1px solid #e8eaf0;
    display: flex;
    align-items: center;
    gap: 10px;
    background: white;
}
.bot-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: #004C8F;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; color: white; font-weight: 700;
    flex-shrink: 0;
}
.chat-title { font-size: 13px; font-weight: 700; color: #004C8F; }
.chat-sub { font-size: 10px; color: #00897b; }
.online-indicator { margin-left: auto; display: flex; align-items: center; gap: 4px; font-size: 10px; color: #00897b; }

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.msg-user {
    align-self: flex-end;
    background: linear-gradient(135deg, #004C8F, #0066CC);
    color: white;
    font-size: 13px;
    padding: 10px 14px;
    border-radius: 14px 14px 2px 14px;
    max-width: 75%;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0,76,143,0.2);
}
.msg-bot {
    align-self: flex-start;
    background: #f4faf8;
    border-left: 3px solid #00D09C;
    font-size: 13px;
    color: #1a1a2e;
    padding: 10px 14px;
    border-radius: 0 14px 14px 0;
    max-width: 80%;
    line-height: 1.5;
}
.msg-source {
    display: inline-block;
    margin-top: 8px;
    padding: 3px 10px;
    background: #e6faf5;
    color: #007a5a;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    text-decoration: none;
    border: 1px solid #b3edd9;
}
.msg-date { font-size: 10px; color: #aaa; margin-top: 4px; }

.quick-panel {
    width: 210px;
    background: #f8f9ff;
    border-left: 1px solid #e8eaf0;
    padding: 14px 12px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex-shrink: 0;
}
.quick-title {
    font-size: 10px;
    font-weight: 700;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px; }
.quick-card {
    background: white;
    border: 1px solid #e8eaf0;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 11px;
    color: #1a1a2e;
    line-height: 1.4;
    cursor: pointer;
}
.quick-card:hover { border-color: #00D09C; }
.quick-cat {
    font-size: 9px;
    color: #00897b;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 3px; }

.disclaimer-bar {
    background: #fff8e1;
    border-top: 1px solid #f9a825;
    padding: 7px 24px;
    font-size: 11px;
    color: #7a6000;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Ask me anything about HDFC Mutual Fund schemes — expense ratio, exit load, minimum SIP, lock-in, benchmark, riskometer, or how to download statements on Groww.",
            "source": None,
            "date": None
        }
    ]

# DEBUG - remove after fixing
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
chroma_path = os.path.join(base_dir, "data", "chroma_db")
st.sidebar.write("Base dir:", base_dir)
st.sidebar.write("Chroma path:", chroma_path)
st.sidebar.write("Chroma path exists:", os.path.exists(chroma_path))
st.sidebar.write("data/ contents:", os.listdir(os.path.join(base_dir, "data")) if os.path.exists(os.path.join(base_dir, "data")) else "NOT FOUND")
try:
    import chromadb
    client = chromadb.PersistentClient(path=chroma_path)
    col = client.get_collection("hdfc_mf_faq")
    st.sidebar.write("Chunks in DB:", col.count())
except Exception as e:
    st.sidebar.write("ChromaDB error:", str(e))

if "chip_query" not in st.session_state:
    st.session_state["chip_query"] = ""

# TOP NAV
st.markdown("""
<div class="top-nav">
    <div class="nav-logo">
        HDFC MF FAQ Assistant
    </div>
    <div class="nav-right">
        <span style="font-size:11px;color:#888;">Powered by</span>
        <a href="https://groww.in/mutual-funds/amc/hdfc-mutual-funds" target="_blank" style="text-decoration:none;">
            <span class="npill npill-groww">Groww</span>
        </a>
        <span style="font-size:11px;color:#ccc;">×</span>
        <a href="https://www.hdfcfund.com" target="_blank" style="text-decoration:none;">
            <span class="npill npill-hdfc">HDFC MF</span>
        </a>
        <span class="npill npill-rag">RAG-Powered</span>
        <span class="npill npill-facts">Facts Only · No Advice</span>
    </div>
</div>
""", unsafe_allow_html=True)

# STATS BAR
st.markdown("""
<div class="stats-bar">
    <div class="stats-left">
        <div><div class="stat-num">7</div><div class="stat-lbl">Schemes</div></div>
        <div><div class="stat-num">49</div><div class="stat-lbl">Facts Indexed</div></div>
        <div><div class="stat-num">28</div><div class="stat-lbl">Verified Sources</div></div>
    </div>
    <div class="stats-right">
        <span class="live-dot"></span>
        Sources last checked: Apr 2026 &nbsp;·&nbsp;
        No investment advice &nbsp;·&nbsp;
        Every answer cited &nbsp;·&nbsp;
        Official sources only
    </div>
</div>
""", unsafe_allow_html=True)

# SCHEME STRIP
st.markdown("""
<div class="scheme-strip">
    <span class="strip-label">Schemes:</span>
    <div class="scheme-chip"><span class="chip-cat">Large Cap</span><span class="chip-name">HDFC Top 100 Fund</span></div>
    <div class="scheme-chip"><span class="chip-cat">Flexi Cap</span><span class="chip-name">HDFC Flexi Cap Fund</span></div>
    <div class="scheme-chip"><span class="chip-cat">ELSS · Tax Saving</span><span class="chip-name">HDFC ELSS Tax Saver Fund</span></div>
    <div class="scheme-chip"><span class="chip-cat">Mid Cap</span><span class="chip-name">HDFC Mid Cap Opp.</span></div>
    <div class="scheme-chip"><span class="chip-cat">Small Cap</span><span class="chip-name">HDFC Small Cap Fund</span></div>
    <div class="scheme-chip"><span class="chip-cat">Hybrid</span><span class="chip-name">HDFC Balanced Adv.</span></div>
    <div class="scheme-chip"><span class="chip-cat">Index · Passive</span><span class="chip-name">HDFC Nifty 50 Index</span></div>
</div>
""", unsafe_allow_html=True)

# MAIN LAYOUT
col_chat, col_quick = st.columns([4, 1])

with col_chat:
    st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chat-top-bar">
        <div class="bot-avatar">MF</div>
        <div>
            <div class="chat-title">HDFC MF FAQ Assistant</div>
            <div class="chat-sub">Facts only · No investment advice</div>
        </div>
        <div class="online-indicator">
            <span class="live-dot"></span> Online
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Build chat messages HTML
    import re
    messages_html = '<div class="chat-messages" id="chat-messages">'
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            messages_html += f'<div class="msg-user">{message["content"]}</div>'
        else:
            content = message["content"]
            last_updated = ""
            if "Last updated from sources:" in content:
                parts = content.split("Last updated from sources:")
                content = parts[0].strip()
                last_updated = "Last updated from sources:" + parts[1].strip()
            
            content = re.sub(
                r'\[([^\]]+)\]\((https?://[^\)]+)\)',
                r'<a class="msg-source" href="\2" target="_blank"> \1</a>',
                content
            )
            date_html = f'<div class="msg-date"> {last_updated}</div>' if last_updated else ""
            messages_html += f'<div class="msg-bot">{content}{date_html}</div>'
    
    messages_html += '</div>'
    messages_html += '<script>const el=document.getElementById("chat-messages");if(el)el.scrollTop=el.scrollHeight;</script>'
    st.markdown(messages_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Ask about any HDFC MF scheme...")
    
    query_to_process = None
    if st.session_state["chip_query"]:
        query_to_process = st.session_state["chip_query"]
        st.session_state["chip_query"] = ""
    elif user_input:
        query_to_process = user_input

    if query_to_process:
        st.session_state["messages"].append({"role": "user", "content": query_to_process})
        try:
            response = answer(query_to_process)
        except Exception:
            response = "Sorry, I could not process your request right now. Please try again later."
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.rerun()

with col_quick:
    st.markdown("""
    <div class="quick-panel">
        <div class="quick-title">Quick Questions</div>
        <div class="quick-card"><div class="quick-cat">Expense Ratio</div>HDFC Flexi Cap expense ratio?</div>
        <div class="quick-card"><div class="quick-cat">Lock-in</div>ELSS lock-in period?</div>
        <div class="quick-card"><div class="quick-cat">Exit Load</div>HDFC Top 100 exit load?</div>
        <div class="quick-card"><div class="quick-cat">Min SIP</div>Minimum SIP for Mid Cap?</div>
        <div class="quick-card"><div class="quick-cat">Riskometer</div>HDFC Small Cap risk level?</div>
        <div class="quick-card"><div class="quick-cat">Benchmark</div>Nifty 50 Index benchmark?</div>
        <div class="quick-card"><div class="quick-cat">Statements</div>Download capital gains on Groww?</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Functional quick question buttons (hidden visually)
    if st.button("Expense ratio of HDFC Flexi Cap Fund?", key="q1"):
        st.session_state["chip_query"] = "What is the expense ratio of HDFC Flexi Cap Fund?"
        st.rerun()
    if st.button("What is the ELSS lock-in period?", key="q2"):
        st.session_state["chip_query"] = "What is the lock-in period for HDFC ELSS Tax Saver Fund?"
        st.rerun()
    if st.button("What is the exit load for HDFC Top 100?", key="q3"):
        st.session_state["chip_query"] = "What is the exit load for HDFC Top 100 Fund?"
        st.rerun()
    if st.button("Minimum SIP for HDFC Mid Cap?", key="q4"):
        st.session_state["chip_query"] = "What is the minimum SIP for HDFC Mid Cap Opportunities Fund?"
        st.rerun()
    if st.button("HDFC Small Cap risk level?", key="q5"):
        st.session_state["chip_query"] = "What is the riskometer of HDFC Small Cap Fund?"
        st.rerun()
    if st.button("HDFC Nifty 50 benchmark?", key="q6"):
        st.session_state["chip_query"] = "What is the benchmark of HDFC Nifty 50 Index Fund?"
        st.rerun()
    if st.button("Download capital gains on Groww?", key="q7"):
        st.session_state["chip_query"] = "How do I download my capital gains statement on Groww?"
        st.rerun()

# DISCLAIMER
st.markdown(f"""
<div class="disclaimer-bar">
     {DISCLAIMER}
</div>
""", unsafe_allow_html=True)
