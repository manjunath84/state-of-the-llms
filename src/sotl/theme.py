# src/sotl/theme.py
THEME_CSS = """
<style>
:root{
  --paper:#FDFCEF; --ink:#0F1419; --accent:#EAFF00; --dark:#1E3A5F;
  --grid:rgba(232,228,208,.4);
}
.stApp{
  background-color:var(--paper);
  background-image:
    linear-gradient(var(--grid) 1px,transparent 1px),
    linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:40px 40px;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  color:var(--ink);
}
[data-testid="stMetric"], .stButton>button{
  border:2px solid var(--ink)!important;
  box-shadow:4px 4px 0 var(--ink)!important;
  background:var(--paper)!important; border-radius:4px;
}
h1,h2,h3{font-weight:800;letter-spacing:-.01em;}
mark,.hl{background:var(--accent);padding:0 .15em;}
</style>
"""
