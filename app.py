import streamlit as st

# TruthLens AI — clean editorial-style interface
# This file contains the website UI only.
# The real prediction model and LIME explainer can be connected later.

st.set_page_config(
    page_title="TruthLens AI",
    page_icon="T",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --page: #f6f7f5;
    --paper: #ffffff;
    --ink: #17211d;
    --muted: #68736d;
    --line: #dfe5e0;
    --accent: #176b52;
    --accent-soft: #eaf3ee;
}

.stApp {
    background: var(--page);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1240px;
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
}

h1, h2, h3 {
    color: var(--ink);
    font-family: 'Manrope', sans-serif;
    letter-spacing: -0.035em;
}

p, label, li {
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background: #eef1ed;
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

.brand-mark {
    display: inline-flex;
    width: 34px;
    height: 34px;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: var(--accent);
    color: white;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 17px;
    margin-right: 9px;
    vertical-align: middle;
}

.brand-name {
    font-family: 'Manrope', sans-serif;
    font-size: 19px;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: var(--ink);
    vertical-align: middle;
}

.topline {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--line);
    padding-bottom: 16px;
    margin-bottom: 36px;
}

.top-meta {
    color: var(--muted);
    font-size: 12px;
    letter-spacing: 0.04em;
}

.eyebrow {
    color: var(--accent);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.page-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(32px, 4vw, 48px);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.055em;
    color: var(--ink);
    max-width: 760px;
    margin-bottom: 14px;
}

.lead {
    color: var(--muted);
    font-size: 16px;
    line-height: 1.7;
    max-width: 720px;
    margin-bottom: 30px;
}

.section-heading {
    font-family: 'Manrope', sans-serif;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: -0.025em;
    margin-bottom: 5px;
}

.section-note {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.55;
    margin-bottom: 15px;
}

.panel {
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 22px;
    min-height: 210px;
}

.panel-kicker {
    color: var(--muted);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.panel-title {
    color: var(--ink);
    font-family: 'Manrope', sans-serif;
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.035em;
    margin-bottom: 8px;
}

.panel-copy {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.65;
}

.rule {
    height: 1px;
    background: var(--line);
    margin: 22px 0;
}

.stTextArea textarea {
    background: #ffffff;
    color: var(--ink);
    border: 1px solid #cfd8d1;
    border-radius: 7px;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    line-height: 1.6;
    padding: 14px;
}

.stTextArea textarea:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px var(--accent);
}

.stButton > button {
    background: var(--accent);
    color: #ffffff;
    border: 1px solid var(--accent);
    border-radius: 7px;
    min-height: 43px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    transition: background 0.15s ease;
}

.stButton > button:hover {
    background: #10533f;
    border-color: #10533f;
    color: #ffffff;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 18px;
    border-bottom: 1px solid var(--line);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--muted);
    border-radius: 0;
    padding: 10px 2px;
    border-bottom: 2px solid transparent;
    font-size: 13px;
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

[data-testid="stAlert"] {
    border-radius: 7px;
}

footer, #MainMenu {
    visibility: hidden;
}

@media (max-width: 800px) {
    .topline {
        gap: 12px;
        align-items: flex-start;
        flex-direction: column;
    }
    .panel {
        padding: 17px;
    }
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(
        '<span class="brand-mark">T</span><span class="brand-name">TruthLens</span>',
        unsafe_allow_html=True
    )
    st.write("")
    st.caption("NEWS VERIFICATION")
    st.divider()
    st.markdown("**Workspace**")
    st.markdown("Article checker")
    st.markdown("Explanation report")
    st.markdown("Project information")
    st.divider()
    st.caption("Prototype version")
    st.markdown(
        '<div style="font-size:12px;color:#68736d;line-height:1.6;">'
        'The classifier and explanation engine will be enabled when the team modules are connected.'
        '</div>',
        unsafe_allow_html=True
    )

# Header
st.markdown("""
<div class="topline">
    <div>
        <span class="brand-mark">T</span><span class="brand-name">TruthLens AI</span>
    </div>
    <div class="top-meta">RESEARCH PROTOTYPE &nbsp; / &nbsp; MODEL NOT CONNECTED</div>
</div>
<div class="eyebrow">Explainable news analysis</div>
<div class="page-title">Look beyond the headline.</div>
<div class="lead">
    Review a news article and understand how an automated classifier evaluates it.
    TruthLens is designed to pair a prediction with a transparent, word-level explanation.
</div>
""", unsafe_allow_html=True)

# Workspace
input_col, result_col = st.columns([1.12, 0.88], gap="large")

with input_col:
    st.markdown('<div class="panel-kicker">01 / ARTICLE INPUT</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Article to review</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Paste the article text below. Include the headline and body when available.</div>',
        unsafe_allow_html=True
    )

    article = st.text_area(
        "Article text",
        placeholder="Paste news article text here...",
        height=280,
        label_visibility="collapsed"
    )
    st.caption(f"{len(article):,} characters")
    analyze = st.button("Review article", use_container_width=True)

    st.markdown(
        '<div class="section-note" style="margin-top:12px;">'
        'For best results, use the full article rather than a headline alone.'
        '</div>',
        unsafe_allow_html=True
    )

with result_col:
    st.markdown('<div class="panel-kicker">02 / REVIEW RESULTS</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Analysis summary</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">The prediction and supporting explanation will be shown here.</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-kicker">PREDICTION</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Waiting for model connection</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-copy">No classification has been generated. Once the trained model is connected, '
        'this area will display its actual output.</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-kicker">EXPLANATION</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Word-level evidence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-copy">LIME highlights and explanatory details will appear here after the explainer is connected.</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

if analyze:
    if article.strip():
        st.info("Article text received. The model is not connected yet, so TruthLens has not classified this article.")
    else:
        st.warning("Enter an article before reviewing it.")

st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
st.markdown(
    '<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;'
    'color:#68736d;font-size:11px;">'
    '<span>TRUTHLENS AI &nbsp; · &nbsp; EXPLAINABLE FAKE NEWS DETECTION</span>'
    '<span>Educational prototype — verify important claims with reliable sources.</span>'
    '</div>',
    unsafe_allow_html=True
)
