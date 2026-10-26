
import streamlit as st
import joblib
import os
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TruthLens AI | News Verification",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- LOAD MODEL ----------------

@st.cache_resource
def load_model():
    model = joblib.load("model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

try:
    model, vectorizer = load_model()
    model_error = None
except Exception as e:
    model = None
    vectorizer = None
    model_error = str(e)



# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "recent_checks" not in st.session_state:
    st.session_state.recent_checks = []

if "last_article" not in st.session_state:
    st.session_state.last_article = ""

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ---------------- EDITORIAL DESIGN ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700;800&display=swap');

    :root {
        --paper: #F7F6F2;
        --white: #FFFFFF;
        --ink: #222222;
        --muted: #6B6B6B;
        --line: #DCDAD4;
        --wine: #8B2635;
        --soft-red: #F8E9EB;
        --soft-green: #E7F2E9;
    }

    .stApp {
        background: var(--paper);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(247,246,242,0.96);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--ink) !important;
        font-family: 'Playfair Display', Georgia, serif !important;
    }

    p, label, li {
        color: var(--ink);
    }

    .masthead {
        text-align: center;
        border-top: 5px solid var(--ink);
        border-bottom: 1px solid var(--ink);
        padding: 18px 0 15px;
        margin-bottom: 12px;
    }

    .brand {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: clamp(34px, 5vw, 52px);
        font-weight: 800;
        letter-spacing: -1.5px;
        line-height: 1.15;
        color: var(--ink);
    }

    .brand span {
        color: var(--wine);
    }

    .tagline {
        font-size: 12px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--muted);
        margin-top: 8px;
    }

    .edition {
        text-align: center;
        color: var(--muted);
        font-size: 11px;
        padding: 8px 0 15px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 24px;
    }

    .section-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--wine);
        border-bottom: 1px solid var(--line);
        padding-bottom: 9px;
        margin-bottom: 15px;
    }

    .hero-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: clamp(34px, 5vw, 53px);
        font-weight: 800;
        line-height: 1.12;
        letter-spacing: -1.2px;
        color: var(--ink);
        margin: 0 0 15px 0;
    }

    .hero-description {
        font-size: 16px;
        line-height: 1.8;
        color: #555555;
        max-width: 720px;
    }

    .paper-card {
        background: var(--white);
        border: 1px solid var(--line);
        padding: 22px;
        margin-bottom: 16px;
    }

    .article-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 22px;
        font-weight: 700;
        line-height: 1.35;
        margin-bottom: 8px;
    }

    .article-meta {
        font-size: 12px;
        color: var(--muted);
        margin-bottom: 10px;
    }

    .verdict {
        padding: 14px 17px;
        border: 1px solid var(--line);
        background: var(--white);
        margin: 12px 0;
    }

    .verdict-fake {
        border-left: 5px solid var(--wine);
        background: var(--soft-red);
    }

    .verdict-real {
        border-left: 5px solid #36734A;
        background: var(--soft-green);
    }

    .verdict-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .verdict-result {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 27px;
        font-weight: 700;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: var(--wine);
        color: white;
        border: 1px solid var(--wine);
        border-radius: 2px;
        padding: 10px 20px;
        font-weight: 600;
        transition: background 0.15s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: #6F1D2A;
        color: white;
        border-color: #6F1D2A;
    }

    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="input"] input {
        background: white;
        border-radius: 2px;
        border-color: #D0CEC7;
        color: var(--ink);
    }

    div[data-baseweb="textarea"] textarea:focus {
        border-color: var(--wine);
        box-shadow: none;
    }

    div[data-testid="stProgress"] > div > div {
        background-color: var(--wine);
    }

    hr {
        border-color: var(--line);
    }

    .footer {
        text-align: center;
        font-size: 12px;
        color: var(--muted);
        border-top: 1px solid var(--ink);
        padding-top: 20px;
        margin-top: 40px;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
    /* Fix article input visibility */
.stTextArea textarea {
    background-color: #fffdf8 !important;
    color: #292521 !important;
    -webkit-text-fill-color: #292521 !important;
    caret-color: #7a263a !important;
    border: 1px solid #d8cec2 !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
}

.stTextArea textarea::placeholder {
    color: #827a72 !important;
    -webkit-text-fill-color: #827a72 !important;
    opacity: 1 !important;
}

.stTextArea textarea:focus {
    border-color: #7a263a !important;
    box-shadow: 0 0 0 2px rgba(122, 38, 58, 0.12) !important;
}

/* Premium TruthLens buttons */
.stButton > button {
    background-color: #7a263a !important;
    color: #ffffff !important;
    border: 1px solid #7a263a !important;
    border-radius: 8px !important;
    padding: 10px 22px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

/* Subtle hover effect */
.stButton > button:hover {
    background-color: #5f1c2c !important;
    border-color: #5f1c2c !important;
    color: #ffffff !important;
    box-shadow: 0 3px 10px rgba(122, 38, 58, 0.18) !important;
}

/* Keyboard focus */
.stButton > button:focus-visible {
    outline: 2px solid #7a263a !important;
    outline-offset: 3px !important;
}

/* --- TruthLens layout refinement --- */

/* Consistent page spacing */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}

/* Navigation buttons: balanced height and text */
.stButton > button {
    min-height: 44px !important;
    padding: 8px 16px !important;
    background-color: #7a263a !important;
    color: #fffdf8 !important;
    border: 1px solid #7a263a !important;
    border-radius: 7px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

/* Fix headline input: warm white background */
.stTextInput input {
    background-color: #fffdf8 !important;
    color: #292521 !important;
    -webkit-text-fill-color: #292521 !important;
    border: 1px solid #d8cec2 !important;
    border-radius: 8px !important;
    min-height: 48px !important;
    padding: 10px 14px !important;
    font-size: 16px !important;
}

/* Headline placeholder */
.stTextInput input::placeholder {
    color: #827a72 !important;
    -webkit-text-fill-color: #827a72 !important;
    opacity: 1 !important;
}

/* Consistent labels */
.stTextInput label,
.stTextArea label {
    color: #292521 !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}

/* Article text area */
.stTextArea textarea {
    background-color: #fffdf8 !important;
    color: #292521 !important;
    -webkit-text-fill-color: #292521 !important;
    border: 1px solid #d8cec2 !important;
    border-radius: 8px !important;
    padding: 14px !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
}

</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------
st.markdown("""
<div class="masthead">
    <div class="brand">TruthLens <span>AI</span></div>
    <div class="tagline">Independent thinking. Informed reading.</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f'<div class="edition">NEWS &nbsp; • &nbsp; MEDIA LITERACY '
    f'&nbsp; • &nbsp; VERIFICATION DESK &nbsp; • &nbsp; '
    f'{datetime.now().strftime("%d %B %Y").upper()}</div>',
    unsafe_allow_html=True
)


# ---------------- NAVIGATION ----------------
nav1, nav2, nav3, nav4 = st.columns([1, 1, 1, 1])


# ---------------- NAVIGATION ----------------
nav_left, nav_right = st.columns([5, 1])


# ---------------- NAVIGATION ----------------
nav1, nav2, nav3, nav4 = st.columns([1, 1, 1, 1])

with nav1:
    if st.button("Home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()

with nav2:
    if st.button("Article Checker", use_container_width=True):
        st.session_state.page = "Article Checker"
        st.rerun()

with nav3:
    if st.button("Explanation Report", use_container_width=True):
        st.session_state.page = "Explanation Report"
        st.rerun()

with nav4:
    if st.button("About", use_container_width=True):
        st.session_state.page = "About"
        st.rerun()

st.markdown("---")


# ---------------- HOME PAGE ----------------
if st.session_state.page == "Home":

    left, right = st.columns([1.7, 1], gap="large")

    with left:
        st.markdown(
            '<div class="section-label">The Verification Desk</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="hero-title">'
            'Question the claim.<br>Check the evidence.'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="hero-description">
        In a world of rapidly spreading information, knowing what to trust
        matters. TruthLens AI uses a machine-learning model to examine
        submitted news articles and estimate whether their content resembles
        examples of real or fake news in its training data.
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button("Verify a News Article →", key="home_check"):
            st.session_state.page = "Article Checker"
            st.rerun()

    with right:
        st.markdown("""
        <div class="paper-card">
            <div class="section-label">Inside TruthLens</div>
            <div class="article-title">A closer look at the news</div>
            <p style="color:#555;line-height:1.7">
            Submit an article, review the model's prediction, and explore
            the words that influenced its decision.
            </p>
            <hr>
            <p><b>01</b> &nbsp; Article analysis</p>
            <p><b>02</b> &nbsp; Prediction and confidence</p>
            <p><b>03</b> &nbsp; Explanation report</p>
            <p style="font-size:12px;color:#777">
            Machine-learning estimates are not independent proof of truth.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown(
        '<div class="section-label">Latest Verification Checks</div>',
        unsafe_allow_html=True
    )

    if st.session_state.recent_checks:
        for item in reversed(st.session_state.recent_checks[-5:]):
            st.markdown('<div class="paper-card">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="article-title">{item["title"]}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="article-meta">{item["time"]} '
                f'&nbsp; • &nbsp; Model assessment</div>',
                unsafe_allow_html=True
            )
            if item["label"] == "Likely Fake":
                st.markdown(
                    '<span style="color:#8B2635;font-weight:700">'
                    'LIKELY FAKE</span>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<span style="color:#36734A;font-weight:700">'
                    'LIKELY REAL</span>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="paper-card">
            <div class="article-title">No checks yet</div>
            <p style="color:#666">
            Your completed article checks will appear here. Start by
            submitting a news article for analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ---------------- ARTICLE CHECKER ----------------
elif st.session_state.page == "Article Checker":

    st.markdown(
        '<div class="section-label">Verification Desk / Article Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-title" style="font-size:38px">'
        'Examine a news article</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Paste the article headline and body below. "
        "The model will compare the text with patterns learned during training."
    )

    if model_error:
        st.error(
            "The model could not be loaded. Make sure model.pkl is in the "
            "same folder as app.py."
        )
        st.code(model_error)

    with st.form("article_form"):
        title = st.text_input(
            "Article headline",
            placeholder="Enter the headline..."
        )

        article = st.text_area(
            "Article text",
            placeholder="Paste the full article text here...",
            height=260
        )

        submitted = st.form_submit_button(
            "Analyse Article",
            use_container_width=True
        )

    if submitted:
        if model is None:
            st.error("The model is unavailable. Check the error above.")
        elif not title.strip() and not article.strip():
            st.warning("Please enter an article headline or article text.")
        else:
            text_to_check = (title.strip() + " " + article.strip()).strip()

            
            
            try:
                text_vector = vectorizer.transform([text_to_check])

                prediction = int(model.predict(text_vector)[0])
                probabilities = model.predict_proba(text_vector)[0]

                # The training script uses 0 = Fake, 1 = Real.
                classes = list(model.classes_)
                predicted_index = classes.index(prediction)
                confidence = float(probabilities[predicted_index]) * 100

                if prediction == 0:
                    label = "Likely Fake"
                    verdict_class = "verdict-fake"
                else:
                    label = "Likely Real"
                    verdict_class = "verdict-real"



                st.session_state.last_article = text_to_check
                st.session_state.last_result = {
                    "label": label,
                    "confidence": confidence,
                    "prediction": prediction
                }

                # Avoid repeatedly adding the same result on every rerun.
                if (
                    not st.session_state.recent_checks
                    or st.session_state.recent_checks[-1]["title"] !=
                    (title.strip() or article.strip()[:70])
                    or st.session_state.recent_checks[-1]["label"] != label
                ):
                    st.session_state.recent_checks.append({
                        "title": title.strip() or article.strip()[:70],
                        "label": label,
                        "confidence": confidence,
                        "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
                    })

                st.markdown("---")
                st.markdown(
                    '<div class="section-label">Assessment Result</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="verdict {verdict_class}">'
                    f'<div class="verdict-label">Model Prediction</div>'
                    f'<div class="verdict-result">{label}</div>'
                    f'<div>Model confidence: {confidence:.1f}%</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.progress(confidence / 100)

                st.caption(
                    "Confidence reflects the model's prediction, not the "
                    "probability that the article is factually true."
                )

                st.warning(
                    "This is an automated estimate, not a fact-check. "
                    "Verify important claims using reliable independent sources."
                )

                if st.button("View Explanation Report →"):
                    st.session_state.page = "Explanation Report"
                    st.rerun()

            except Exception as e:
                st.error("The article could not be analysed.")
                st.code(str(e))


# ---------------- EXPLANATION REPORT ----------------
elif st.session_state.page == "Explanation Report":

    st.markdown(
        '<div class="section-label">Verification Desk / Model Transparency</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-title" style="font-size:38px">'
        'Understanding the prediction</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.last_article or not st.session_state.last_result:
        st.info(
            "No article has been analysed yet. Visit Article Checker "
            "and submit an article first."
        )

        if st.button("Go to Article Checker"):
            st.session_state.page = "Article Checker"
            st.rerun()

    else:
        result = st.session_state.last_result

        st.markdown('<div class="paper-card">', unsafe_allow_html=True)
        st.markdown("**Article assessed**")
        st.write(st.session_state.last_article[:700])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            f"**Model prediction:** {result['label']}  \n"
            f"**Model confidence:** {result['confidence']:.1f}%"
        )

        try:
            from lime.lime_text import LimeTextExplainer

            explainer = LimeTextExplainer(
                class_names=["Fake", "Real"]
            )

            explanation = explainer.explain_instance(
                st.session_state.last_article,
                model.predict_proba,
                num_features=10,
                num_samples=1000
            )

            st.markdown("### Words influencing the prediction")
            st.caption(
                "LIME estimates how individual words affect this model's "
                "prediction for the submitted text. These are not verified "
                "evidence that a claim is true or false."
            )

            for word, weight in explanation.as_list():
                col1, col2 = st.columns([2, 3])

                with col1:
                    st.write(f"**{word}**")

                with col2:
                    st.write(f"Influence: {weight:+.3f}")
                    st.progress(min(abs(float(weight)), 1.0))

        except ImportError:
            st.warning(
                "LIME is not installed. Open your terminal and run: "
                "python -m pip install lime"
            )
        except Exception as e:
            st.error("Could not generate the explanation report.")
            st.code(str(e))


# ---------------- ABOUT PAGE ----------------
elif st.session_state.page == "About":

    st.markdown(
        '<div class="section-label">About the Project</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-title" style="font-size:38px">'
        'Building a more informed reader</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="paper-card">
        <div class="article-title">What is TruthLens AI?</div>
        <p style="line-height:1.8;color:#555">
        TruthLens AI is an educational news-classification project designed
        to demonstrate how machine learning can identify patterns associated
        with fake and real news articles.
        </p>
        <hr>
        <div class="article-title">How it works</div>
        <p style="line-height:1.8;color:#555">
        The project uses a text-processing pipeline based on TF-IDF and
        Logistic Regression. It learns from labelled examples and applies
        those learned patterns to text submitted by the user.
        </p>
        <hr>
        <div class="article-title">Important limitations</div>
        <p style="line-height:1.8;color:#555">
        The model may misclassify articles, perform poorly on new topics,
        or reflect biases in its training data. It does not independently
        verify sources, dates, quotations, or supporting evidence.
        Always consult trustworthy sources before deciding whether a claim
        is true.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Technology used**")
    st.write(
        "Python · Streamlit · Pandas · Scikit-learn · TF-IDF · "
        "Logistic Regression · LIME"
    )


# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    <b>TruthLens AI</b><br>
    Independent thinking. Informed reading.<br><br>
    An educational machine-learning project. Predictions require
    independent verification.
</div>
""", unsafe_allow_html=True)
 