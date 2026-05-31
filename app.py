# app.py
import pandas as pd
import plotly.express as px
import streamlit as st

from sotl.config import settings
from sotl.data import load_models
from sotl.recommend import recommend
from sotl.theme import THEME_CSS

st.set_page_config(page_title="State of the LLMs", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)


@st.cache_data
def _models():
    return load_models(settings.models_csv)


def beat_scatter(df):
    st.header("① The price collapse")
    st.caption("Frontier quality is getting cheaper fast. Bubble size = context window.")
    labs = sorted(df["lab"].dropna().unique().tolist())
    picked = st.multiselect("Filter by lab", labs, default=labs)
    view = df[df["lab"].isin(picked)].copy() if picked else df.copy()
    for c in ["price_out", "mmlu_pro", "context_window"]:
        view[c] = pd.to_numeric(view[c], errors="coerce")
    view = view.dropna(subset=["price_out", "mmlu_pro", "context_window"])
    fig = px.scatter(
        view, x="price_out", y="mmlu_pro", size="context_window",
        color="lab", hover_name="name", log_x=True,
        labels={"price_out": "$ / 1M output tokens", "mmlu_pro": "MMLU-Pro"},
    )
    fig.update_layout(paper_bgcolor="#FDFCEF", plot_bgcolor="#FDFCEF", font_color="#0F1419")
    st.plotly_chart(fig, use_container_width=True)


def beat_picker(df):
    st.header("② Pick a model")
    c1, c2, c3 = st.columns(3)
    task = c1.selectbox("Task", ["coding", "general / reasoning"])
    budget = c2.slider("Max $ / 1M output tokens", 0.5, 30.0, 10.0, 0.5)
    prefer_eff = c3.toggle("Prefer faster/cheaper on ties", value=True)
    rec = recommend(
        df,
        task="coding" if task == "coding" else "general",
        max_price_out=budget,
        prefer_efficient=prefer_eff,
    )
    if rec.pick is None:
        st.warning("No model fits that budget — raise the slider.")
        return
    st.success(f"**Pick: {rec.pick}** — best {rec.score_col} at ≤ ${budget:.1f}/1M out")
    with st.expander("Show the math", expanded=True):
        st.dataframe(
            rec.reason_rows[["name", "lab", "price_out", rec.score_col]],
            use_container_width=True, hide_index=True,
        )


def beat_finale(df):
    st.header("③ Equivalent API cost")
    st.info("Built in a later task.")


def main():
    df = _models()
    st.title("State of the LLMs")
    st.caption("A model-selection data story · Gen Academy Week 1")
    tab1, tab2, tab3 = st.tabs(["① Price collapse", "② Pick a model", "③ Equivalent API cost"])
    with tab1:
        beat_scatter(df)
    with tab2:
        beat_picker(df)
    with tab3:
        beat_finale(df)


if __name__ == "__main__":
    main()
