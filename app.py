import streamlit as st
import joblib
from pathlib import Path
from datetime import datetime
from lime.lime_text import LimeTextExplainer
import plotly.express as px

# ---------------- PAGE SETUP ----------------
BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="TruthLens AI | News Intelligence",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- DESIGN ----------------
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700;800&display=swap');
:root {
  --paper:#f5f2ec; --card:#fffefa; --ink:#262421; --muted:#77716a;
  --wine:#812b3c; --line:#e4ded4; --green:#397451;
}
.stApp {background:var(--paper); color:var(--ink); font-family:'DM Sans',sans-serif;}
.block-container {max-width:1180px; padding-top:1.2rem; padding-bottom:3rem;}
[data-testid="stHeader"] {background:transparent;}
h1,h2,h3 {font-family:'Playfair Display',Georgia,serif!important; color:var(--ink)!important;}
p,li,label {color:var(--ink);}
.brandline {display:flex;align-items:center;justify-content:space-between;border-top:5px solid var(--ink);border-bottom:1px solid var(--ink);padding:16px 2px 13px;margin-bottom:7px;}
.brand {font-family:'Playfair Display',serif;font-weight:800;font-size:clamp(30px,4vw,43px);letter-spacing:-1.3px;color:var(--ink);}
.brand span {color:var(--wine);}
.brandnote {font-size:10px;letter-spacing:1.8px;text-transform:uppercase;color:var(--muted);text-align:right;line-height:1.8;}
.edition {font-size:10px;letter-spacing:1.7px;text-transform:uppercase;color:var(--muted);padding:10px 0 18px;border-bottom:1px solid var(--line);margin-bottom:22px;}
.eyebrow {font-size:10px;letter-spacing:2px;text-transform:uppercase;font-weight:700;color:var(--wine);border-bottom:1px solid var(--line);padding-bottom:9px;margin:12px 0 16px;}
.hero {font-family:'Playfair Display',serif;font-size:clamp(34px,4.5vw,53px);line-height:1.08;letter-spacing:-1.1px;margin:0 0 13px;color:var(--ink);}
.sub {font-size:15px;line-height:1.8;color:#625d56;max-width:720px;}
.paper {background:var(--card);border:1px solid var(--line);border-radius:13px;padding:22px 23px;margin:8px 0 16px;box-shadow:0 7px 24px rgba(40,30,20,.045);}
.kicker {font-size:10px;text-transform:uppercase;letter-spacing:1.6px;color:var(--muted);font-weight:700;}
.metric-label {font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:var(--muted);font-weight:700;}
.result-real {border-left:5px solid var(--green);background:#edf4ee;padding:20px;border-radius:9px;}
.result-fake {border-left:5px solid var(--wine);background:#f8ecee;padding:20px;border-radius:9px;}
.result-title {font-family:'Playfair Display',serif;font-size:30px;font-weight:700;color:var(--ink);}
.small-muted {font-size:12px;color:var(--muted);line-height:1.7;}
div.stButton>button,div.stFormSubmitButton>button {background:var(--wine);color:white;border:1px solid var(--wine);border-radius:8px;padding:10px 17px;font-weight:700;min-height:43px;}
div.stButton>button:hover,div.stFormSubmitButton>button:hover {background:#65202e;color:white;border-color:#65202e;}
.stTextInput input,.stTextArea textarea {background:#fffefa!important;color:#292521!important;-webkit-text-fill-color:#292521!important;border:1px solid #d9d1c6!important;border-radius:9px!important;}
.stTextArea textarea {line-height:1.7!important;padding:13px!important;}
.stTextInput label,.stTextArea label {font-weight:700;color:#34312d!important;}
[data-testid="stProgress"]>div>div {background:var(--wine);}
[data-testid="stMetric"] {background:var(--card);border:1px solid var(--line);padding:13px;border-radius:10px;}
[data-testid="stStatusWidget"] {background:var(--card);border:1px solid var(--line);border-radius:10px;}
.footer {border-top:1px solid var(--ink);margin-top:42px;padding-top:17px;text-align:center;color:var(--muted);font-size:11px;line-height:1.8;}
div[data-testid="stForm"] {background:var(--card);padding:20px;border:1px solid var(--line);border-radius:13px;}
#MainMenu,footer {visibility:hidden;}
</style>
""")

# ---------------- MODEL ----------------
@st.cache_resource(show_spinner="Loading the detection model…")
def load_model():
    model = joblib.load(BASE_DIR / "model.pkl")
    vectorizer = joblib.load(BASE_DIR / "vectorizer.pkl")
    return model, vectorizer

try:
    model, vectorizer = load_model()
    model_error = None
except Exception as exc:
    model, vectorizer = None, None
    model_error = str(exc)

# Keep this mapping consistent with the model training labels.
# Verify 0=Fake and 1=Real against the training script before presenting results.
def label_for(class_value):
    return "Likely Fake" if int(class_value) == 0 else "Likely Real"

# Cache the LIME explainer object; it is reused for later reports.
@st.cache_resource
def get_lime_explainer(class_names):
    return LimeTextExplainer(class_names=list(class_names), random_state=42)

# Cache the generated weights by article and predicted class. Underscore-prefixed
# model arguments are intentionally excluded from Streamlit's cache hashing.
@st.cache_data(show_spinner=False, ttl=3600)
def make_lime_explanation(article_text, predicted_index, class_names, _model, _vectorizer):
    lime_explainer = get_lime_explainer(tuple(class_names))

    def predict_probabilities(texts):
        return _model.predict_proba(_vectorizer.transform(texts))

    explanation = lime_explainer.explain_instance(
        text_instance=article_text,
        classifier_fn=predict_probabilities,
        labels=tuple(range(len(class_names))),
        num_features=8,
        num_samples=250,
    )
    return explanation.as_list(label=int(predicted_index))

# ---------------- SESSION STATE ----------------
defaults = {
    "page": "Home",
    "recent_checks": [],
    "last_article": "",
    "last_title": "",
    "last_result": None,
    "last_explanation": None,
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------- HEADER ----------------
st.html(f"""
<div class="brandline">
  <div class="brand">TruthLens <span>AI</span></div>
  <div class="brandnote">NEWS INTELLIGENCE<br>INDEPENDENT THINKING · INFORMED READING</div>
</div>
<div class="edition">VERIFICATION DESK &nbsp; • &nbsp; MEDIA LITERACY &nbsp; • &nbsp; {datetime.now().strftime('%d %B %Y').upper()}</div>
""")

pages = ["Home", "Article Checker", "Explanation Report", "About"]
nav_cols = st.columns(4)
for col, page_name in zip(nav_cols, pages):
    with col:
        if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
            st.session_state.page = page_name
            st.rerun()

st.divider()

# ---------------- HOME ----------------
if st.session_state.page == "Home":
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.markdown('<div class="eyebrow">THE VERIFICATION DESK</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero">Question the claim.<br>Examine the text.</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub">TruthLens AI examines submitted news text and estimates whether it resembles examples of real or fake news in its training data.</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Analyse a news article  →", key="home_start"):
            st.session_state.page = "Article Checker"
            st.rerun()
    with right:
        st.markdown("""
        <div class="paper">
          <div class="eyebrow">INSIDE TRUTHLENS</div>
          <h3>A clearer way to inspect a claim</h3>
          <p class="small-muted">Submit text, review the model estimate, and inspect the language that influenced the prediction.</p>
          <hr><p><b>01</b> &nbsp; Text classification</p>
          <p><b>02</b> &nbsp; Confidence estimate</p>
          <p><b>03</b> &nbsp; LIME explanation</p>
          <p class="small-muted">A model prediction is not independent proof of truth.</p>
        </div>""", unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">RECENT CHECKS</div>', unsafe_allow_html=True)
    if st.session_state.recent_checks:
        for item in reversed(st.session_state.recent_checks[-5:]):
            with st.container(border=True):
                st.write(f"**{item['title']}**")
                st.caption(f"{item['time']} · {item['label']} · {item['confidence']:.1f}% model confidence")
    else:
        st.info("No checks yet. Your recent article analyses will appear here.")

# ---------------- ARTICLE CHECKER ----------------
elif st.session_state.page == "Article Checker":
    st.markdown('<div class="eyebrow">VERIFICATION DESK / ARTICLE ANALYSIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero">Examine a news article</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Paste the headline and article text. The model compares the submitted text with patterns learned during training.</div>', unsafe_allow_html=True)

    if model_error:
        st.error("The model could not be loaded. Keep model.pkl and vectorizer.pkl beside app.py.")
        st.code(model_error)

    with st.form("analysis_form"):
        title = st.text_input("Article headline", placeholder="Enter the headline…")
        article = st.text_area("Article text", placeholder="Paste the full article text here…", height=240)
        submitted = st.form_submit_button("Run analysis  →", use_container_width=True)

    if submitted:
        # Remove the previous article result before processing this submission.
        st.session_state.last_result = None
        st.session_state.last_explanation = None
        st.session_state.last_article = ""
        st.session_state.last_title = ""

        text_to_check = (title.strip() + " " + article.strip()).strip()

        if not text_to_check:
            st.warning("Please enter a headline or article text first.")
        elif model is None:
            st.error("The model is unavailable. Resolve the loading error above.")
        else:
            try:
                with st.status("Analysing article…", expanded=True) as status:
                    st.write("Preparing the submitted text")
                    vector = vectorizer.transform([text_to_check])

                    st.write("Running the classification model")
                    prediction = int(model.predict(vector)[0])
                    probs = model.predict_proba(vector)[0]
                    classes = list(model.classes_)
                    confidence = float(probs[classes.index(prediction)]) * 100
                    label = label_for(prediction)

                    result = {
                        "label": label,
                        "confidence": confidence,
                        "prediction": prediction,
                    }

                    st.session_state.last_article = text_to_check
                    st.session_state.last_title = title.strip() or text_to_check[:90]
                    st.session_state.last_result = result
                    st.session_state.last_explanation = None

                    st.session_state.recent_checks.append({
                        "title": st.session_state.last_title,
                        "label": label,
                        "confidence": confidence,
                        "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    })
                    st.session_state.recent_checks = st.session_state.recent_checks[-20:]

                    status.update(
                        label="Article analysis complete",
                        state="complete",
                        expanded=False,
                    )

                css_class = "result-fake" if prediction == 0 else "result-real"
                st.markdown(
                    f'<div class="{css_class}"><div class="kicker">MODEL ASSESSMENT</div>'
                    f'<div class="result-title">{label}</div>'
                    f'<div>Model confidence: <b>{confidence:.1f}%</b></div></div>',
                    unsafe_allow_html=True,
                )
                st.progress(confidence / 100)
                st.caption(
                    "Confidence describes the model's confidence in its classification, "
                    "not the probability that the article is factually true."
                )
                st.warning(
                    "This is an automated text classification, not a fact-check. "
                    "Verify important claims using reliable independent sources."
                )

                if st.button("Generate explanation report  →"):
                    st.session_state.page = "Explanation Report"
                    st.rerun()

            except Exception as exc:
                st.error("The article could not be analysed.")
                st.exception(exc)

    # Keep the last result visible after navigation back to this page.
    elif st.session_state.last_result:
        result = st.session_state.last_result
        css_class = "result-fake" if result["prediction"] == 0 else "result-real"
        st.markdown(
            f'<div class="{css_class}"><div class="kicker">LATEST MODEL ASSESSMENT</div>'
            f'<div class="result-title">{result["label"]}</div>'
            f'<div>Model confidence: <b>{result["confidence"]:.1f}%</b></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Open explanation report  →"):
            st.session_state.page = "Explanation Report"
            st.rerun()

# ---------------- EXPLANATION REPORT ----------------
elif st.session_state.page == "Explanation Report":
    st.markdown('<div class="eyebrow">VERIFICATION DESK / MODEL TRANSPARENCY</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero">Why did the model decide this?</div>', unsafe_allow_html=True)

    if not st.session_state.last_article or not st.session_state.last_result:
        st.info("No article has been analysed yet. Run an analysis first.")
        if st.button("Go to Article Checker"):
            st.session_state.page = "Article Checker"
            st.rerun()
    else:
        result = st.session_state.last_result
        col_article, col_metrics = st.columns([1.45, 1])
        with col_article:
            st.markdown('<div class="paper"><div class="kicker">ARTICLE ASSESSED</div></div>', unsafe_allow_html=True)
            st.write(st.session_state.last_title)
            excerpt = st.session_state.last_article[:500]
            st.caption(excerpt + ("…" if len(st.session_state.last_article) > 500 else ""))
        with col_metrics:
            st.metric("Model prediction", result["label"])
            st.metric("Model confidence", f"{result['confidence']:.1f}%")

        st.markdown('<div class="eyebrow">LANGUAGE INFLUENCE</div>', unsafe_allow_html=True)
        st.caption("LIME estimates which words influenced the selected model prediction. Generate it once; the result is cached for this article.")
        if st.session_state.last_explanation is None:
            if st.button("Generate explanation", use_container_width=True):
                if model is None:
                    st.error("The model is unavailable.")
                else:
                    try:
                        predicted_index = list(model.classes_).index(int(result["prediction"]))
                        class_names = [label_for(c) for c in model.classes_]
                        with st.status("Preparing the explanation…", expanded=True) as status:
                            st.write("Sampling variations of the article text")
                            st.write("Measuring how the model responds to those variations")
                            weights = make_lime_explanation(
                                st.session_state.last_article,
                                predicted_index,
                                tuple(class_names),
                                model,
                                vectorizer,
                            )
                            st.session_state.last_explanation = weights
                            status.update(label="Explanation generated", state="complete", expanded=False)
                        st.rerun()
                    except Exception as exc:
                        st.error("Could not generate the explanation report.")
                        st.exception(exc)
        else:
            weights = st.session_state.last_explanation
            positive = sum(abs(float(weight)) for _, weight in weights if float(weight) > 0)
            negative = sum(abs(float(weight)) for _, weight in weights if float(weight) < 0)
            if positive + negative > 0:
                chart_data = {
                    "Influence": ["Supports predicted class", "Pushes away from predicted class"],
                    "Magnitude": [positive, negative],
                }
                fig = px.pie(
                    chart_data,
                    names="Influence",
                    values="Magnitude",
                    hole=0.58,
                    color="Influence",
                    color_discrete_map={
                        "Supports predicted class": "#812b3c",
                        "Pushes away from predicted class": "#c9b9a8",
                    },
                )
                fig.update_traces(textposition="inside", textinfo="percent", sort=False)
                fig.update_layout(
                    height=260,
                    margin=dict(t=8, b=8, l=8, r=8),
                    legend_title_text="",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#262421"),
                )
                chart_col, spacer_col = st.columns([1, 1])
                with chart_col:
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={"displayModeBar": False},
                    )

            st.markdown("#### Words that influenced the prediction")
            max_weight = max((abs(float(weight)) for _, weight in weights), default=0) or 1

            for word, weight in weights:
                value = float(weight)
                bar_value = min(abs(value) / max_weight, 1.0)

                if value > 0:
                    st.markdown(
                        f"**{word}** · <span style='color:#397451'>{value:+.3f}</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption("Supports the predicted class")
                else:
                    st.markdown(
                        f"**{word}** · <span style='color:#812b3c'>{value:+.3f}</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption("Pushes away from the predicted class")

                st.progress(bar_value)
            st.caption("The donut chart compares the total magnitude of positive and negative LIME weights. It does not measure factual accuracy.")
            if st.button("Regenerate explanation"):
                st.session_state.last_explanation = None
                st.rerun()
        st.warning("LIME explains the model's behaviour, not whether the article's claims are factually true.")

# ---------------- ABOUT ----------------
else:
    st.markdown('<div class="eyebrow">ABOUT THE PROJECT</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero">A tool for more informed reading</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="paper">
      <h3>What is TruthLens AI?</h3>
      <p class="small-muted">TruthLens AI is an educational machine-learning project that classifies submitted news text using patterns learned from labelled examples.</p>
      <hr><h3>How it works</h3>
      <p class="small-muted">The application transforms text using TF-IDF and passes it to a Logistic Regression classifier. LIME provides a local explanation of words that influenced an individual prediction.</p>
      <hr><h3>Limitations</h3>
      <p class="small-muted">The model can misclassify content, may not generalise to new topics, and does not independently verify sources, dates, quotations, or evidence. Use it as a learning and screening aid, not a final authority.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("**Technology:** Python · Streamlit · Scikit-learn · TF-IDF · Logistic Regression · LIME · Plotly")

st.markdown(
    '<div class="footer"><b>TRUTHLENS AI</b><br>Independent thinking · Informed reading'
    '<br>Educational machine-learning project. Predictions require independent verification.</div>',
    unsafe_allow_html=True,
)
