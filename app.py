import streamlit as st
import re
from src.rag import answer
from src.prompts import DISCLAIMER

st.set_page_config(
    page_title="HDFC MF FAQ Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Ask me anything about HDFC Mutual Fund schemes — expense ratio, exit load, minimum SIP, lock-in, benchmark, riskometer, or how to download statements on Groww.",
        }
    ]

if "chip_query" not in st.session_state:
    st.session_state["chip_query"] = ""

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
    white-space: nowrap;
    flex-shrink: 0;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: nowrap;
}
.npill {
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    white-space: nowrap;
}
.npill-groww { background: #e6faf5; color: #007a5a; border: 1px solid #00D09C; text-decoration: none; }
.npill-hdfc { background: #fef0f0; color: #c0131a; border: 1px solid #ED232A; text-decoration: none; }
.npill-rag { background: #e8f0fe; color: #1a56db; border: 1px solid #c5d8fd; }
.npill-facts { background: #e6faf5; color: #007a5a; border: 1px solid #00D09C; }
.desktop-only { display: inline-block; }

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
.stats-right { font-size: 11px; color: #a0b8d4; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.live-dot { width: 7px; height: 7px; border-radius: 50%; background: #00D09C; display: inline-block; flex-shrink: 0; }

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
    height: 420px;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    scroll-behavior: smooth;
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

.disclaimer-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #fff8e1;
    border-top: 1px solid #f9a825;
    padding: 6px 24px;
    font-size: 11px;
    color: #7a6000;
    z-index: 9999;
}

@media (max-width: 768px) {
    .npill-rag, .npill-facts { display: none !important; }
    .top-nav { padding: 8px 12px; }
    .nav-logo { font-size: 12px; }
    .npill { font-size: 10px !important; padding: 2px 7px !important; }
    
    .stats-bar {
        padding: 8px 12px !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 6px !important;
    }
    .stats-left {
        gap: 20px !important;
        width: 100% !important;
    }
    .stat-num { font-size: 18px !important; }
    .stat-lbl { font-size: 9px !important; }
    .stats-right {
        display: none !important;
    }
    
    .scheme-strip { padding: 6px 10px; }
    .scheme-chip { min-width: 90px; padding: 4px 8px; }
    .chip-cat { font-size: 8px; }
    .chip-name { font-size: 10px; }
    .disclaimer-fixed { font-size: 10px; padding: 5px 12px; }
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
<div class="top-nav">
    <div class="nav-logo">&#128202; HDFC MF FAQ Assistant</div>
    <div class="nav-right">
        <a href="https://groww.in/mutual-funds/amc/hdfc-mutual-funds" 
           target="_blank" style="text-decoration:none;">
            <span class="npill npill-groww">&#8599; Groww</span>
        </a>
        <span style="color:#ccc;font-size:11px;">&#215;</span>
        <a href="https://www.hdfcfund.com" 
           target="_blank" style="text-decoration:none;">
            <span class="npill npill-hdfc">&#8599; HDFC MF</span>
        </a>
        <span class="npill npill-rag">&#9889; RAG-Powered</span>
        <span class="npill npill-facts">&#9989; Facts Only</span>
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
        Sources last checked: Apr 2026 &nbsp;&#183;&nbsp;
        No investment advice &nbsp;&#183;&nbsp;
        Every answer cited &nbsp;&#183;&nbsp;
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
    <div class="scheme-chip"><span class="chip-cat">ELSS &middot; Tax Saving</span><span class="chip-name">HDFC ELSS Tax Saver</span></div>
    <div class="scheme-chip"><span class="chip-cat">Mid Cap</span><span class="chip-name">HDFC Mid Cap Opp.</span></div>
    <div class="scheme-chip"><span class="chip-cat">Small Cap</span><span class="chip-name">HDFC Small Cap Fund</span></div>
    <div class="scheme-chip"><span class="chip-cat">Hybrid</span><span class="chip-name">HDFC Balanced Adv.</span></div>
    <div class="scheme-chip"><span class="chip-cat">Index &middot; Passive</span><span class="chip-name">HDFC Nifty 50 Index</span></div>
</div>
""", unsafe_allow_html=True)

# MAIN LAYOUT
col_chat, col_quick = st.columns([4, 1])

with col_chat:
    st.markdown("""
    <div class="chat-top-bar">
        <div class="bot-avatar">MF</div>
        <div>
            <div class="chat-title">HDFC MF FAQ Assistant</div>
            <div class="chat-sub">Facts only &middot; No investment advice</div>
        </div>
        <div class="online-indicator"><span class="live-dot"></span> Online</div>
    </div>
    """, unsafe_allow_html=True)

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
                r'<a class="msg-source" href="\2" target="_blank">&#128279; \1</a>',
                content
            )
            date_html = f'<div class="msg-date">&#128336; {last_updated}</div>' if last_updated else ""
            messages_html += f'<div class="msg-bot">{content}{date_html}</div>'
    messages_html += '</div>'
    messages_html += '<script>const el=document.getElementById("chat-messages");if(el)el.scrollTop=el.scrollHeight;</script>'
    st.markdown(messages_html, unsafe_allow_html=True)

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
    # Only render on desktop - detected via screen width workaround
    # We use st.query_params to detect if mobile was set by JS
    is_mobile = st.query_params.get("mobile", "false") == "true"
    
    if not is_mobile:
        questions = [
            ("EXPENSE RATIO", "Flexi Cap expense ratio?", 
             "What is the expense ratio of HDFC Flexi Cap Fund?"),
            ("LOCK-IN", "ELSS lock-in period?", 
             "What is the lock-in period for HDFC ELSS Tax Saver Fund?"),
            ("EXIT LOAD", "Top 100 exit load?", 
             "What is the exit load for HDFC Top 100 Fund?"),
            ("MIN SIP", "Min SIP Mid Cap?", 
             "What is the minimum SIP for HDFC Mid Cap Opportunities Fund?"),
            ("RISKOMETER", "Small Cap risk level?", 
             "What is the riskometer of HDFC Small Cap Fund?"),
            ("BENCHMARK", "Nifty 50 benchmark?", 
             "What is the benchmark of HDFC Nifty 50 Index Fund?"),
            ("STATEMENTS", "Capital gains Groww?", 
             "How do I download capital gains statement on Groww?"),
        ]
        st.markdown(
            '<p style="font-size:10px;font-weight:700;color:#888;'
            'text-transform:uppercase;letter-spacing:0.08em;'
            'margin:14px 0 8px 4px;">Quick Questions</p>',
            unsafe_allow_html=True
        )
        for cat, label, query in questions:
            st.markdown(
                f'<p style="font-size:9px;font-weight:700;color:#00897b;'
                f'text-transform:uppercase;letter-spacing:0.05em;'
                f'margin:6px 0 2px 2px;">{cat}</p>',
                unsafe_allow_html=True
            )
            if st.button(label, key=f"q_{cat}", use_container_width=True):
                st.session_state["chip_query"] = query
                st.rerun()

st.markdown("""
<script>
(function() {
    function setMobile() {
        const isMobile = window.innerWidth <= 768;
        const url = new URL(window.parent.location.href);
        const current = url.searchParams.get('mobile');
        const val = isMobile ? 'true' : 'false';
        if (current !== val) {
            url.searchParams.set('mobile', val);
            window.parent.history.replaceState({}, '', url.toString());
        }
    }
    setMobile();
    window.addEventListener('resize', setMobile);
})();
</script>
""", unsafe_allow_html=True)

# DISCLAIMER
st.markdown("""
<div class="disclaimer-fixed">
    &#9888;&#65039; Facts-only assistant. No investment advice.
    Mutual fund investments are subject to market risks.
    Please read all scheme-related documents carefully.
    Consult a SEBI-registered advisor before investing.
</div>
""", unsafe_allow_html=True)