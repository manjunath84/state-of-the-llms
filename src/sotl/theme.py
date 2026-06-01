# src/sotl/theme.py
# Brutalist accent layer on top of .streamlit/config.toml's native palette.
# config.toml sets the cream/ink/blue base + sidebar; this adds the 40px grid,
# electric-yellow accents, 2px-ink borders + hard shadows, and header hierarchy.
# NOTE: theme.py is a module — Streamlit will NOT reimport it on rerun. Restart
# the server after editing.
THEME_CSS = """
<style>
:root{
  --paper:#FDFCEF; --ink:#0F1419; --accent:#EAFF00; --dark:#1E3A5F;
  --grid:rgba(232,228,208,.5); --code-bg:#F5F2DA; --rule:#d9d4b8; --mute:#666;
}

/* Page: cream + 40px grid */
.stApp{
  background-color:var(--paper);
  background-image:
    linear-gradient(var(--grid) 1px,transparent 1px),
    linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:40px 40px;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  color:var(--ink);
}

/* Title: big, tight, with a yellow underline bar */
h1{
  font-weight:900!important; letter-spacing:-.02em!important; line-height:1.02!important;
  font-size:3rem!important; margin-bottom:.1em!important;
}
h1::after{
  content:""; display:block; width:84px; height:10px; margin-top:.18em;
  background:var(--accent); border:2px solid var(--ink);
}
h2{font-weight:850!important; letter-spacing:-.015em!important; margin-top:.2em!important;}
h3{font-weight:800!important; letter-spacing:-.01em!important;}

/* Highlight + inline code */
mark,.hl{background:var(--accent); padding:0 .18em; box-decoration-break:clone;}
code{background:var(--code-bg)!important; color:var(--ink)!important;
     padding:.05em .35em; border-radius:3px;}

/* Tabs: brutalist pill row; selected = ink chip with yellow text */
.stTabs [data-baseweb="tab-list"]{gap:.5rem; border-bottom:2px solid var(--ink);}
.stTabs [data-baseweb="tab"]{
  background:var(--paper); border:2px solid var(--ink); border-bottom:none;
  border-radius:6px 6px 0 0; padding:.35rem .9rem!important; font-weight:700;
}
.stTabs [aria-selected="true"]{background:var(--ink)!important; color:var(--accent)!important;}
.stTabs [aria-selected="true"] p{color:var(--accent)!important; font-weight:800;}

/* Metric card: hard brutalist shadow, yellow value */
[data-testid="stMetric"]{
  border:2px solid var(--ink); box-shadow:6px 6px 0 var(--ink);
  background:var(--paper); border-radius:6px; padding:1rem 1.2rem;
}
[data-testid="stMetricValue"]{font-weight:900!important; color:var(--ink);}
[data-testid="stMetricLabel"] p{color:var(--mute)!important; font-weight:600;}

/* Buttons (the chips): brutalist, press-in on hover */
.stButton>button{
  border:2px solid var(--ink)!important; box-shadow:4px 4px 0 var(--ink)!important;
  background:var(--paper)!important; color:var(--ink)!important; border-radius:6px;
  font-weight:700!important; transition:transform .04s,box-shadow .04s;
}
.stButton>button:hover{
  background:var(--accent)!important; transform:translate(2px,2px);
  box-shadow:2px 2px 0 var(--ink)!important;
}

/* Takeaway box (st.success): cream w/ ink border + yellow left bar, NOT green */
[data-testid="stAlertContentSuccess"], div[data-testid="stNotification"]{}
.stAlert{border:2px solid var(--ink)!important; border-radius:6px!important;
         box-shadow:4px 4px 0 var(--ink)!important;}
[data-baseweb="notification"]{
  background:var(--paper)!important; border-left:10px solid var(--accent)!important;
}
.stAlert p{color:var(--ink)!important; font-weight:600;}

/* Sidebar: warm cream, ink right-border, headers underlined */
[data-testid="stSidebar"]{
  background:var(--code-bg)!important; border-right:2px solid var(--ink);
}
[data-testid="stSidebar"] h3{
  border-bottom:2px solid var(--ink); padding-bottom:.2em; margin-bottom:.4em;
}

/* Dashed section rule under captions, tighter caption color */
.stCaption, [data-testid="stCaptionContainer"]{color:var(--mute)!important;}

/* Expander: bordered to match the brutalist language */
[data-testid="stExpander"]{border:2px solid var(--ink)!important; border-radius:6px;
  box-shadow:3px 3px 0 var(--ink);}
</style>
"""
