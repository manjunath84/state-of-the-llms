# app.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from sotl.chips import CHIP_IDS, CHIP_LABELS, run_chip
from sotl.config import settings
from sotl.data import load_models, load_pricing, load_usage
from sotl.frontier import pareto_frontier
from sotl.narrate import takeaway
from sotl.recommend import recommend
from sotl.theme import THEME_CSS
from sotl.trust import trust_summary
from sotl.usage import (
    by_model_detail,
    cost_components,
    filter_scope,
    total_spend,
)

st.set_page_config(page_title="State of the LLMs", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

MONTHLY_PLAN_USD = 100

# Narrators on the configured OpenAI-compatible endpoint (default OpenRouter,
# which serves both open and closed models under one key). The app argues open
# models caught up, so an OPEN model is the default narrator — but you can switch
# to a closed model live and compare. Either way the narration gate (narrate.py)
# rejects any number the model invents, so the choice is about prose, not safety.
# Default = DeepSeek V3, a current flagship OPEN model — and itself one of the
# "open caught up" models on the chart, so it literally narrates its own story.
# Listed first → it's the selectbox default. Closed GPT models are offered for
# live comparison; the narration gate keeps every option numerically honest.
NARRATORS = {
    "DeepSeek V3 (open)": "deepseek/deepseek-chat",
    "Qwen 2.5 72B (open)": "qwen/qwen-2.5-72b-instruct",
    "Llama 3.3 70B (open)": "meta-llama/llama-3.3-70b-instruct",
    "GPT-4o (closed)": "openai/gpt-4o",
    "GPT-4o mini (closed)": "openai/gpt-4o-mini",
}


@st.cache_data
def _models():
    return load_models(settings.models_csv)


@st.cache_data
def _usage():
    # usage.csv is already scoped to THIS Week-1 project by scripts/derive_usage.py
    return load_usage(settings.usage_csv)


@st.cache_data
def _pricing():
    # list prices — joined onto usage tokens to split cost into components
    return load_pricing(settings.pricing_csv)


def _chip_rail(df):
    st.markdown("**Ask the data** — click a question:")
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
        line = takeaway(cid, res.headline, settings, model=model)
        # st.success renders markdown — escape literal $ so a "$0.28" pair isn't
        # parsed as LaTeX math (the same bug that garbled the finale caption).
        st.success(line.replace("$", "\\$"))
        st.caption(f"narrated by `{model}` · numbers computed in pandas, not by the model")
        with st.expander("Show the rows behind it"):
            st.dataframe(res.frame, use_container_width=True, hide_index=True)


def beat_scatter(df):
    st.header("① The price collapse")
    st.markdown(
        "**The story in one line:** open models like DeepSeek now hit ~80% on real-world "
        "coding for *pennies*, while the best closed model (Opus) leads at ~89% but costs "
        "**~25× more** per token. Cheap is no longer weak."
    )
    st.caption(
        "Each dot is a model. X = price per 1M output tokens (log scale). "
        "Y = SWE-bench Verified, a real-world coding benchmark. Bubble size = context window. "
        "Bottom-left is cheap, top is capable — watch how close the cheap dots have climbed."
    )
    # Coerce the plotted columns, then build the lab filter from rows that can
    # actually plot — so selecting a lab with no plottable rows isn't a dead click.
    plot = df.copy()
    for c in ["price_out", "swe_bench", "context_window"]:
        plot[c] = pd.to_numeric(plot[c], errors="coerce")
    plot = plot.dropna(subset=["price_out", "swe_bench", "context_window"])
    labs = sorted(plot["lab"].dropna().unique().tolist())
    picked = st.multiselect("Filter by lab", labs, default=labs)
    view = plot[plot["lab"].isin(picked)].copy() if picked else plot.copy()
    # Label only the story-critical extremes (cheapest + most capable + most
    # expensive) so the mid-cluster doesn't smear into overlapping text.
    view["label"] = ""
    if not view.empty:
        for idx in {view["price_out"].idxmin(), view["price_out"].idxmax(),
                    view["swe_bench"].idxmax()}:
            view.loc[idx, "label"] = view.loc[idx, "name"]
    fig = px.scatter(
        view, x="price_out", y="swe_bench", size="context_window",
        color="lab", text="label", hover_name="name", log_x=True,
        labels={"price_out": "Price — $ / 1M output tokens (log)",
                "swe_bench": "SWE-bench Verified (%)", "lab": "Lab"},
    )
    fig.update_traces(
        textposition="top center", textfont_size=12, textfont_color="#0F1419",
        marker=dict(line=dict(width=1.5, color="#0F1419")),
    )
    # The price-for-skill frontier: the models you literally cannot beat on both
    # price AND coding skill at once. The line makes "the price collapse" visible
    # — everything above/left is a deal, everything below/right is dominated.
    front = pareto_frontier(view)
    if len(front) >= 2:
        fig.add_trace(go.Scatter(
            x=front["price_out"], y=front["swe_bench"], mode="lines",
            line=dict(color="#0F1419", width=2, dash="dash"),
            name="best price-for-skill frontier", hoverinfo="skip",
        ))
    fig.update_layout(
        paper_bgcolor="#FDFCEF", plot_bgcolor="rgba(0,0,0,0)", font_color="#0F1419",
        margin=dict(t=20, b=0, l=0, r=0), legend_title_text="Lab",
        xaxis=dict(gridcolor="#E8E4D0"), yaxis=dict(gridcolor="#E8E4D0"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "The dashed line is the **price-for-skill frontier** — the models you "
        "can't beat on both price and coding skill at once. Dots below/right of "
        "it are dominated: something else is cheaper *and* better."
    )
    _chip_rail(view)


def beat_picker(df):
    st.header("② Pick a model")
    st.markdown(
        "**Tell it your constraints, it shows its work.** Pick a task and a budget; "
        "it ranks the models that fit and explains *why* — no black box."
    )
    c1, c2, c3 = st.columns(3)
    task = c1.selectbox("What's the job?", ["coding", "general / reasoning"])
    budget = c2.slider("Max price (\\$ / 1M output tokens)", 0.5, 30.0, 10.0, 0.5)
    prefer_eff = c3.toggle("Prefer cheaper on ties", value=True)
    rec = recommend(
        df,
        task="coding" if task == "coding" else "general",
        max_price_out=budget,
        prefer_efficient=prefer_eff,
    )
    metric_label = "SWE-bench (coding)" if rec.score_col == "swe_bench" else "MMLU-Pro (reasoning)"
    if rec.pick is None:
        st.warning(
            f"No model has a **{metric_label}** score within that budget. "
            "Try raising the slider, or switch the task — coding has the densest data."
        )
        return
    st.success(f"**Pick: {rec.pick}** — best {metric_label} at ≤ \\${budget:.1f} / 1M output")
    # Narrate the pick through the SAME gated narrator the chips use, so tab ②
    # isn't the only silent beat. The summary carries every number; the gate in
    # narrate.py rejects any figure the model invents (guardrail #3).
    pick_row = rec.reason_rows.iloc[0]
    pick_score = float(pick_row[rec.score_col])
    pick_price = float(pick_row["price_out"])
    short_metric = "SWE-bench" if rec.score_col == "swe_bench" else "MMLU-Pro"
    summary = (
        f"{rec.pick} is the top {short_metric} model at or under ${budget:.1f} per 1M "
        f"output tokens: it scores {pick_score:.1f} on {short_metric} at ${pick_price:.2f} "
        "per 1M output tokens."
    )
    model = st.session_state.get("narrator_model", settings.narration_model)
    line = takeaway("picker", summary, settings, model=model).replace("$", "\\$")
    st.caption(f"🗣️ {line}  ·  narrated by `{model}`, numbers computed in pandas")
    with st.expander("Show the math — every candidate it ranked", expanded=True):
        st.dataframe(
            rec.reason_rows[["name", "lab", "price_out", rec.score_col]],
            use_container_width=True, hide_index=True,
            column_config={
                "name": "Model", "lab": "Lab",
                "price_out": st.column_config.NumberColumn("$ / 1M out", format="$%.2f"),
                rec.score_col: metric_label,
            },
        )


_COMPONENT_LABELS = {
    "cache_write": "Cache write", "output": "Output",
    "cache_read": "Cache read", "input": "Input",
}
_COMPONENT_COLORS = {
    "Cache write": "#EAFF00",  # the surprise — most of the bill — highlighted
    "Output": "#1E3A5F", "Cache read": "#888", "Input": "#d9d4b8",
}


def beat_finale(_models_df):
    st.header("③ What did it cost to build THIS app?")
    u_all = _usage()
    pricing = _pricing()

    # Scope toggle: the app folder alone vs the whole Week-1 effort. Both are
    # honest answers to "this app" — the difference is whether planning counts.
    scope = st.radio(
        "What counts as building \"this app\"?",
        ["Whole Week-1 effort (incl. planning)", "Just the app folder"],
        horizontal=True,
    )
    app_only = scope.startswith("Just")
    u = filter_scope(u_all, app_only=app_only)
    total = total_spend(u)

    st.metric("Equivalent API cost at published list prices", f"${total:,.2f}")
    # NOTE: st.caption renders markdown — every literal $ must be escaped as \$,
    # or Streamlit treats the text between two $ as LaTeX math (the garbled-line bug).
    st.caption(
        f"Built on a flat \\${MONTHLY_PLAN_USD}/mo Claude plan — so the real out-of-pocket "
        "cost was the subscription, not per-token. But the tokens that built it would cost "
        f"about \\${total:,.2f} at API list prices. The token counts are real — measured "
        "from the actual build transcripts. The dollar figure is a notional list-price "
        "conversion, **not** money spent."
    )

    # --- Reveal 1: which model actually ran (the Opus-vs-Sonnet story) ---
    detail = by_model_detail(u)
    if not detail.empty:
        top = detail.iloc[0]
        st.markdown(
            f"**I kept Opus 4.8 as my default model.** Claude Code offered to route coding "
            f"to the cheaper Sonnet 4.6 — but with Opus left as the default, "
            f"**{top['share_pct']:.1f}% of the build ran on `{top['model']}`**, not Sonnet. "
            "That one default is where the money went:"
        )
        st.dataframe(
            detail, hide_index=True, use_container_width=True,
            column_config={
                "model": "Model",
                "output_tokens": st.column_config.NumberColumn("Output tokens", format="%d"),
                "est_cost_usd": st.column_config.NumberColumn("Est. cost", format="$%.2f"),
                "share_pct": st.column_config.NumberColumn("Share of cost", format="%.1f%%"),
            },
        )

    # --- Reveal 2: where the dollars go (output vs cache) ---
    comp = cost_components(u, pricing)
    comp["label"] = comp["component"].map(_COMPONENT_LABELS)
    comp = comp.sort_values("cost", ascending=False)
    st.markdown(
        "**And most of that isn't 'thinking' — it's cache.** A long session re-caches its "
        "growing context every turn, so **cache writes**, not output, dominate the bill:"
    )
    fig = px.bar(
        comp, x="label", y="cost", color="label",
        color_discrete_map=_COMPONENT_COLORS,
        labels={"cost": "Equivalent API cost ($)", "label": ""},
    )
    fig.update_traces(marker_line_color="#0F1419", marker_line_width=1.5)
    fig.update_layout(
        paper_bgcolor="#FDFCEF", plot_bgcolor="#FDFCEF", font_color="#0F1419",
        margin=dict(t=10, b=0, l=0, r=0), showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    top_model = detail.iloc[0]["model"] if not detail.empty else "n/a"
    st.markdown(
        f"> **Every token that built the app you're looking at would cost "
        f"<mark>\\${total:,.2f}</mark> at API list prices** — mostly `{top_model}`, mostly "
        f"cache. It was built on a flat \\${MONTHLY_PLAN_USD}/mo plan: that's the recursive "
        "close — the tool measuring AI cost, measuring itself.",
        unsafe_allow_html=True,
    )


def main():
    df = _models()
    with st.sidebar:
        st.subheader("🗣️ Narrator")
        choice = st.selectbox("Who writes the takeaways?", list(NARRATORS))
        st.session_state["narrator_model"] = NARRATORS[choice]
        st.caption(
            "Default is an **open-source** model — fitting, since the app argues open "
            "models caught up. Switch to a closed model (GPT) to compare the prose. "
            "Either way it only narrates; the numbers are computed in pandas, and a "
            "validation gate rejects any figure the model invents."
        )
        st.subheader("🔒 Data Trust")
        s = trust_summary(df)
        counts = s["counts"]
        lab = int(counts.get("reported_by_lab", 0))
        third = int(counts.get("third_party", 0))
        parts = []
        if lab:
            parts.append(f"{lab} lab-reported")
        if third:
            parts.append(f"{third} third-party")
        st.markdown(
            f"Every metric is sourced. **{' · '.join(parts) or 'all sourced'}**, "
            f"verified **{s['oldest_verified']}**."
        )
        if s["missing_swe_bench"]:
            st.caption(
                f"{s['missing_swe_bench']} model(s) have no public SWE-bench score yet — "
                "shown in tables, hidden from the coding chart rather than guessed."
            )
    st.title("State of the LLMs")
    st.markdown(
        "#### A model-selection data story for builders · Gen Academy Week 1\n"
        "Three steps: **see** the price-vs-skill landscape → **pick** a model for your job → "
        "**measure** what AI-assisted building actually costs (using this app's own logs)."
    )
    tab1, tab2, tab3 = st.tabs(
        ["① See the landscape", "② Pick a model", "③ Cost to build this app"]
    )
    with tab1:
        beat_scatter(df)
    with tab2:
        beat_picker(df)
    with tab3:
        beat_finale(df)


if __name__ == "__main__":
    main()
