import streamlit as st
import os
import httpx
import matplotlib.pyplot as plt
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
}


def get_sop_feedback(user_input):
    prompt = (
        "You are an SOP feedback assistant. Analyze the Statement of Purpose (SOP) draft below and provide detailed, constructive feedback. "
        "Your feedback should address content strength, structure, clarity, tone, and specificity. "
        "Do not rewrite the SOP. Only provide critical, helpful feedback.\n\nSOP:\n" + user_input
    )
    payload = {
        "model": "deepseek/deepseek-r1",
        "messages": [
            {"role": "system", "content": "You are an SOP feedback assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 900,
    }
    response = httpx.post(API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.json()}"


def get_ai_authenticity_score(user_input):
    prompt = (
        "You are an AI Authenticity evaluator. Score this SOP from 0 to 5 (5 = very human-like) on:\n"
        "Voice, Emotional Resonance, Personal Insight, Generic Language (lower is better), Believability.\n"
        "Return in JSON: {\"Voice\": 3, \"Emotion\": 2, \"Insight\": 4, \"Generic\": 1, \"Believability\": 3}\n\n"
        "SOP:\n" + user_input
    )
    payload = {
        "model": "deepseek/deepseek-r1",
        "messages": [
            {"role": "system", "content": "You are an AI authenticity evaluator."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
    }
    response = httpx.post(API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        import json
        content = response.json()["choices"][0]["message"]["content"]
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            scores = json.loads(json_str)
            return scores
        except Exception:
            return None
    else:
        return None


def plot_authenticity_scores(scores):
    categories = [
        "Voice & Authenticity",
        "Emotional Resonance",
        "Personal Insight",
        "Less Generic Language",
        "Overall Believability",
    ]
    mapping = {
        "Voice": "Voice & Authenticity",
        "Emotion": "Emotional Resonance",
        "Insight": "Personal Insight",
        "Generic": "Less Generic Language",
        "Believability": "Overall Believability",
    }
    values = [scores.get(k, 0) for k in mapping.keys()]
    # Flip Generic: higher is better
    values[3] = 5 - values[3]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(categories, values, color="#006699")
    ax.set_ylim(0, 5)
    ax.set_ylabel("Score (0–5)")
    ax.set_title("🧠 AI Authenticity Self-Check", fontsize=14, fontweight='bold')
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f"{val:.1f}", ha='center', fontsize=9)
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    st.pyplot(fig)


def main():
    st.set_page_config(
        page_title="Jokings Educare — SOP Coach",
        page_icon="📝",
        layout="centered"
    )

    # Inject custom styles
    st.markdown("""
        <style>
            body {
                background-color: #f4f6f9;
                color: #2c3e50;
                font-family: 'Segoe UI', sans-serif;
            }
            .feedback-box {
                background-color: #eef6fb;
                border-left: 5px solid #007acc;
                padding: 20px;
                border-radius: 10px;
                animation: fadeIn 1s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    """, unsafe_allow_html=True)

    # Layout: logo and title
    col1, col2 = st.columns([1, 5])
    with col1:
        try:
            st.image("jokings_logo.png", width=140)
        except:
            st.warning("⚠️ Logo not found — place 'jokings_logo.png' in the same folder as this app.")

    with col2:
        st.markdown(
            "<h1 style='color:#007acc; margin-bottom: 0;'>Jokings Educare</h1>"
            "<h4 style='margin-top: 0;'>SOP Feedback & AI Authenticity Coach</h4>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    sop_text = st.text_area(
        "📄 Paste your Statement of Purpose (SOP) below:",
        height=250,
        placeholder="Start typing or paste your SOP draft here..."
    )

    if st.button("🧠 Analyze SOP"):
        if not sop_text.strip():
            st.warning("Please paste your SOP first.")
            return

        with st.spinner("Analyzing your SOP draft..."):
            feedback = get_sop_feedback(sop_text)
            st.subheader("🔍 Constructive Feedback")
            st.markdown(f"<div class='feedback-box'>{feedback}</div>", unsafe_allow_html=True)

            scores = get_ai_authenticity_score(sop_text)
            if scores:
                st.subheader("🤖 AI Authenticity Scoring")
                plot_authenticity_scores(scores)
            else:
                st.error("Could not compute AI authenticity scores. Try again later or reduce the SOP length.")

if __name__ == "__main__":
    main()
