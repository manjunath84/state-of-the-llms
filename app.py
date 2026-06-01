# app.py
import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from sotl.chips import CHIP_IDS, CHIP_LABELS, run_chip
from sotl.config import settings
from sotl.data import load_models, load_pricing, load_usage
from sotl.frontier import pareto_frontier
from sotl.narrate import gate_demo, takeaway
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
        _gate_demo_panel(res.headline)
        with st.expander("Show the rows behind it"):
            st.dataframe(res.frame, use_container_width=True, hide_index=True)


def _gate_demo_panel(summary: str):
    # The differentiator made visible: prove the narrator can't slip in a fabricated
    # NUMBER. Deterministically inject a fake score, then show the SAME gate that runs
    # on every live takeaway catching it. (It validates numbers, not prose — named honestly.)
    with st.expander("🔬 Number-validation gate — can the model sneak in a fake number?"):
        demo = gate_demo(summary)
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("**🔓 Ungated** — what a raw model could ship:")
            st.error(demo.ungated.replace("$", "\\$"))
        with g2:
            st.markdown("**🔒 Gated** — what this app actually ships:")
            st.success(demo.gated.replace("$", "\\$"))
        if demo.caught:
            st.caption(
                f"`{demo.injected}` is in the sentence but not in the computed data → "
                "**rejected**, replaced with the sourced line. The same check runs on every "
                "takeaway above. (It validates numbers, not prose — so it's a *number* gate.)"
            )


def beat_scatter(df):
    st.header("① The price collapse")
    st.markdown(
        "**The story in one line:** open models like DeepSeek now hit ~77% on real-world "
        "coding for *pennies*, while the best closed model (Opus) leads at ~89% but costs "
        "**~29× more** per token. On a level harness the gap is small; the price gap is huge."
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
    # Label the story-critical extremes (cheapest + most capable + most expensive)
    # PLUS the two heroes the narrative names, so they're never unlabeled even when
    # they aren't an extreme. Keeps the mid-cluster clean without losing the leads.
    HERO_LABELS = {"DeepSeek-V4-Pro", "Claude Opus 4.8"}
    view["label"] = ""
    if not view.empty:
        for idx in {view["price_out"].idxmin(), view["price_out"].idxmax(),
                    view["swe_bench"].idxmax()}:
            view.loc[idx, "label"] = view.loc[idx, "name"]
        hero = view["name"].isin(HERO_LABELS)
        view.loc[hero, "label"] = view.loc[hero, "name"]
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
            line=dict(color="#0F1419", width=3, dash="dash"),
            name="best price-for-skill frontier", hoverinfo="skip",
        ))
        # On-chart label so the line reads without the caption (demo legibility).
        mid = front.iloc[len(front) // 2]
        fig.add_annotation(
            x=math.log10(mid["price_out"]), y=mid["swe_bench"],
            text="price–skill frontier", showarrow=True, arrowhead=0, ax=18, ay=-26,
            font=dict(size=12, color="#0F1419"), bgcolor="#EAFF00",
            bordercolor="#0F1419", borderwidth=1.5, borderpad=2,
        )
    # Explicit $ ticks on the log axis. Plotly's default log ticks print bare
    # minor magnitudes ("7 8 9 1 2 3 … 10 2 3") with no $, which is unreadable —
    # replace with a handful of labelled dollar gridlines spanning the data.
    PRICE_TICKS = [0.25, 0.5, 1, 2, 5, 10, 20, 50]
    fig.update_layout(
        paper_bgcolor="#FDFCEF", plot_bgcolor="rgba(0,0,0,0)", font_color="#0F1419",
        margin=dict(t=20, b=0, l=0, r=0), legend_title_text="Lab",
        xaxis=dict(
            gridcolor="#E8E4D0", tickfont=dict(size=13),
            title="Price — $ per 1M output tokens · log scale · ← cheaper / pricier →",
            tickmode="array", tickvals=PRICE_TICKS,
            ticktext=[(f"${v:g}" if v >= 1 else f"${v:.2f}") for v in PRICE_TICKS],
        ),
        yaxis=dict(gridcolor="#E8E4D0", tickfont=dict(size=13)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "The dashed line is the **price-for-skill frontier** — the models you "
        "can't beat on both price and coding skill at once. Dots below/right of "
        "it are dominated: something else is cheaper *and* better. "
        "All SWE-bench scores are vals.ai's independent bash-only harness, so every dot "
        "is measured the same way."
    )
    # Priced but not independently benchmarked: an honest home for models vals.ai
    # hasn't scored yet, so they're disclosed rather than guessed onto the chart.
    nob = df.copy()
    nob["_price"] = pd.to_numeric(nob["price_out"], errors="coerce")
    nob["_swe"] = pd.to_numeric(nob["swe_bench"], errors="coerce")
    nob = nob[nob["_price"].notna() & nob["_swe"].isna()]
    if not nob.empty:
        with st.expander(f"➕ {len(nob)} model(s) priced but not yet independently benchmarked"):
            st.caption(
                "Published price, but no vals.ai SWE-bench Verified score yet — listed "
                "here rather than guessed onto the chart (guardrail: never invent a number)."
            )
            st.dataframe(
                nob[["name", "lab", "price_out", "is_open"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "name": "Model", "lab": "Lab",
                    "price_out": st.column_config.NumberColumn("$ / 1M out", format="$%.2f"),
                    "is_open": "Open?",
                },
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
        rows = rec.reason_rows.copy()
        # Make the ranking legible: "value" = skill per dollar (score ÷ price). This
        # is the number the efficient-rank actually sorts on — show it, don't hide it.
        rows["value"] = (pd.to_numeric(rows[rec.score_col], errors="coerce")
                         / pd.to_numeric(rows["price_out"], errors="coerce"))
        st.dataframe(
            rows[["name", "lab", "price_out", rec.score_col, "value"]],
            use_container_width=True, hide_index=True,
            column_config={
                "name": "Model", "lab": "Lab",
                "price_out": st.column_config.NumberColumn("$ / 1M out", format="$%.2f"),
                rec.score_col: metric_label,
                "value": st.column_config.NumberColumn(
                    "Value (pts/$)", format="%.1f",
                    help="Skill per dollar: benchmark score ÷ price. Higher = more skill per $."),
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

    with st.expander("🔎 Evidence — where this number comes from"):
        tok = int(pd.to_numeric(
            u[["input_tokens", "output_tokens", "cache_creation_tokens", "cache_read_tokens"]]
            .stack(), errors="coerce").sum())
        projs = ", ".join(f"`{x}`" for x in sorted(u["project"].unique()))
        st.markdown(
            f"- **{len(u)} usage rows**, measured from this project's real Claude Code "
            f"transcripts, across: {projs}\n"
            f"- **{tok:,} tokens** total (input + output + cache)\n"
            f"- Last derived **{u['date'].max()}** by `scripts/derive_usage.py`\n"
            "- **No raw transcript text, message content, or file paths are committed** — "
            "only these scrubbed aggregates (guardrail #4). Re-run the script to refresh."
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
    # Lead with the hook so even a casual repo viewer sees the differentiator before
    # the ordinary chart: this app measures its OWN build cost.
    _u = _usage()
    _detail = by_model_detail(_u)
    _share = _detail.iloc[0]["share_pct"] if not _detail.empty else 0.0
    st.markdown(
        f"<div style='display:inline-block;background:#0F1419;color:#EAFF00;"
        f"font-weight:800;border:2px solid #0F1419;box-shadow:4px 4px 0 #1E3A5F;"
        f"border-radius:6px;padding:.5rem .9rem;margin:.2rem 0 .6rem'>"
        f"💸 This app measured its own build: <span style='color:#fff'>"
        f"&#36;{total_spend(_u):,.0f}</span> at API list prices · "
        f"<span style='color:#fff'>{_share:.1f}% ran on Opus</span> → see tab ③</div>",
        unsafe_allow_html=True,
    )
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
