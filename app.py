# app.py
import pandas as pd
import plotly.express as px
import streamlit as st

from sotl.chips import CHIP_IDS, CHIP_LABELS, run_chip
from sotl.config import settings
from sotl.data import load_models, load_usage
from sotl.narrate import takeaway
from sotl.recommend import recommend
from sotl.theme import THEME_CSS
from sotl.trust import trust_summary
from sotl.usage import by_model as usage_by_model
from sotl.usage import total_spend

st.set_page_config(page_title="State of the LLMs", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

MONTHLY_PLAN_USD = 20

# Open-source narrators on the configured OpenAI-compatible endpoint (default
# OpenRouter). The app argues open models caught up, so an open model narrates it.
NARRATORS = {
    "Llama 3.1 8B (open)": "meta-llama/llama-3.1-8b-instruct",
    "Llama 3.3 70B (open)": "meta-llama/llama-3.3-70b-instruct",
    "Qwen 2.5 7B (open)": "qwen/qwen-2.5-7b-instruct",
}


@st.cache_data
def _models():
    return load_models(settings.models_csv)


@st.cache_data
def _usage():
    # usage.csv is already scoped to THIS Week-1 project by scripts/derive_usage.py
    return load_usage(settings.usage_csv)


def _chip_rail(df):
    st.caption("Ask the data:")
    cols = st.columns(len(CHIP_IDS))
    for col, cid in zip(cols, CHIP_IDS, strict=True):
        if col.button(CHIP_LABELS[cid], key=f"chip_{cid}", use_container_width=True):
            st.session_state["active_chip"] = cid
    cid = st.session_state.get("active_chip")
    if cid and df.empty:
        st.info("No rows in the current filter — clear a lab to see a takeaway.")
    elif cid:
        res = run_chip(cid, df)  # safe: df non-empty (run_chip uses .iloc[0])
        model = st.session_state.get("narrator_model", settings.narration_model)
        st.markdown(f"**{takeaway(cid, res.headline, settings, model=model)}**")
        st.caption(f"narrated by `{model}`")
        with st.expander("Show the rows behind it"):
            st.dataframe(res.frame, use_container_width=True, hide_index=True)


def beat_scatter(df):
    st.header("① The price collapse")
    st.caption(
        "Frontier coding skill is getting cheaper fast. Y = SWE-bench Verified "
        "(real-world coding); bubble size = context window."
    )
    labs = sorted(df["lab"].dropna().unique().tolist())
    picked = st.multiselect("Filter by lab", labs, default=labs)
    view = df[df["lab"].isin(picked)].copy() if picked else df.copy()
    for c in ["price_out", "swe_bench", "context_window"]:
        view[c] = pd.to_numeric(view[c], errors="coerce")
    view = view.dropna(subset=["price_out", "swe_bench", "context_window"])
    fig = px.scatter(
        view, x="price_out", y="swe_bench", size="context_window",
        color="lab", hover_name="name", log_x=True,
        labels={"price_out": "$ / 1M output tokens", "swe_bench": "SWE-bench Verified (%)"},
    )
    fig.update_layout(paper_bgcolor="#FDFCEF", plot_bgcolor="#FDFCEF", font_color="#0F1419")
    st.plotly_chart(fig, use_container_width=True)
    _chip_rail(view)


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


def beat_finale(_models_df):
    st.header("③ Equivalent API cost — to build THIS app")
    u = _usage()
    total = total_spend(u)
    bym = usage_by_model(u)
    st.metric("Equivalent API cost to build this app (published list prices)", f"${total:,.2f}")
    st.caption(
        f"Built on a flat ${MONTHLY_PLAN_USD}/mo Claude plan — the tokens that built "
        f"this very Week-1 app (brainstorm, plan, code) would cost ~${total:,.2f} at API "
        "list prices. Token counts are real (measured from transcripts); the dollar "
        "figure is a notional list-price conversion, **not** actual spend."
    )
    st.plotly_chart(
        px.bar(bym, x="model", y="est_cost_usd",
               labels={"est_cost_usd": "equiv. API cost ($)"}).update_layout(
            paper_bgcolor="#FDFCEF", plot_bgcolor="#FDFCEF", font_color="#0F1419"),
        use_container_width=True,
    )
    top = bym.iloc[0]["model"] if not bym.empty else "n/a"
    st.markdown(
        f"> **Every token that built the app you're looking at — brainstorm, plan, and "
        f"code — would cost <mark>${total:,.2f}</mark> at API list prices** (mostly "
        f"{top}). I built it on a flat ${MONTHLY_PLAN_USD}/mo plan.",
        unsafe_allow_html=True,
    )


def main():
    df = _models()
    with st.sidebar:
        st.subheader("🗣️ Narrator")
        choice = st.selectbox("Who writes the takeaways?", list(NARRATORS))
        st.session_state["narrator_model"] = NARRATORS[choice]
        st.caption(
            "Open-source narrators via OpenRouter — the app argues open models "
            "caught up, so an open model narrates it."
        )
        s = trust_summary(df)
        st.subheader("🔒 Data Trust")
        st.write(f"Sources verified as of **{s['oldest_verified']}** (oldest).")
        st.write({k: int(v) for k, v in s["counts"].items()})
        if s["missing_swe_bench"]:
            st.warning(f"{s['missing_swe_bench']} model(s) missing SWE-bench.")
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
