"""Render Readme.md -> docs/index.html for GitHub Pages.

Run: python build_site.py
Output: docs/index.html, docs/charts/*.svg, docs/.nojekyll
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
README = ROOT / "Readme.md"
DOCS = ROOT / "docs"
CHARTS_SRC = ROOT / "charts"

SITE_TITLE = "The Hidden Math Behind Every Decision You Make"
SITE_DESCRIPTION = (
    "Six mental models — Expected Value, Base Rates, Sunk Cost, Bayes, "
    "Survivorship Bias, Kelly Criterion — for thinking clearly under uncertainty."
)
REPO_URL = "https://github.com/mthewessen/HiddenMathOfDecisions"


# Markdown $$...$$ blocks and $...$ inlines must survive markdown processing so
# KaTeX auto-render can pick them up. Use placeholders then restore.
def protect_math(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}

    def repl_block(m: re.Match) -> str:
        key = f"@@MATHBLOCK{len(placeholders)}@@"
        placeholders[key] = m.group(0)
        return key

    def repl_inline(m: re.Match) -> str:
        key = f"@@MATHINLINE{len(placeholders)}@@"
        placeholders[key] = m.group(0)
        return key

    # Block math: $$ ... $$ (single or multi-line, non-greedy)
    text = re.sub(r"\$\$.+?\$\$", repl_block, text, flags=re.DOTALL)
    # Inline math: $...$ on one line, not crossing newlines, not preceded by backslash
    text = re.sub(r"(?<!\\)\$[^\$\n]+?\$", repl_inline, text)
    return text, placeholders


def restore_math(html: str, placeholders: dict[str, str]) -> str:
    for key, original in placeholders.items():
        html = html.replace(key, original)
    return html


def render_readme() -> str:
    text = README.read_text(encoding="utf-8")
    text, math = protect_math(text)
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "attr_list", "sane_lists"],
        extension_configs={"toc": {"permalink": False}},
    )
    html = md.convert(text)
    html = restore_math(html, math)
    # GitHub-style task lists: <li>[ ] x</li> -> checkbox
    html = re.sub(
        r"<li>\[ \] ",
        '<li class="task"><input type="checkbox" disabled /> ',
        html,
    )
    html = re.sub(
        r"<li>\[[xX]\] ",
        '<li class="task"><input type="checkbox" checked disabled /> ',
        html,
    )
    # Make external links open in new tab
    html = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', html)
    return html


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{description}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous" />
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous" onload="renderMathInElement(document.body, {{ delimiters: [{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}], throwOnError:false }});"></script>

<link rel="stylesheet" href="style.css" />
</head>
<body>
<header class="site-header">
  <div class="container">
    <a class="brand" href="./">Hidden Math of Decisions</a>
    <nav>
      <a href="{repo_url}" target="_blank" rel="noopener">GitHub</a>
      <a href="{repo_url}/blob/main/decision_math.py" target="_blank" rel="noopener">Python</a>
      <a href="{repo_url}/blob/main/decision_math_formulas.xlsx" target="_blank" rel="noopener">Excel</a>
      <button id="theme-toggle" type="button" aria-label="Toggle theme">🌓</button>
    </nav>
  </div>
</header>

<main class="container article">
{body}
</main>

<footer class="site-footer">
  <div class="container">
    <p>Built from <a href="{repo_url}/blob/main/Readme.md" target="_blank" rel="noopener">Readme.md</a> · Charts rendered as SVG · Math via <a href="https://katex.org" target="_blank" rel="noopener">KaTeX</a></p>
  </div>
</footer>

<script src="script.js"></script>
</body>
</html>
"""


STYLE_CSS = """:root {
  --bg: #fbfaf7;
  --bg-elev: #ffffff;
  --fg: #1a1a1a;
  --fg-muted: #555;
  --accent: #2F5496;
  --accent-2: #C00000;
  --border: #e6e3dc;
  --code-bg: #f4f1ea;
  --max-w: 760px;
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}

[data-theme="dark"] {
  --bg: #14171c;
  --bg-elev: #1b1f25;
  --fg: #e8e6e1;
  --fg-muted: #9ea3ad;
  --accent: #7aa7e6;
  --accent-2: #ff7676;
  --border: #2a2f37;
  --code-bg: #11141a;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: var(--font-sans);
  font-size: 17px;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

.container {
  max-width: var(--max-w);
  margin: 0 auto;
  padding: 0 1.25rem;
}

.site-header {
  position: sticky;
  top: 0;
  background: color-mix(in srgb, var(--bg) 92%, transparent);
  backdrop-filter: saturate(180%) blur(10px);
  border-bottom: 1px solid var(--border);
  z-index: 10;
}
.site-header .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  max-width: 1080px;
}
.brand {
  font-weight: 700;
  color: var(--fg);
  text-decoration: none;
  letter-spacing: -0.01em;
}
.site-header nav {
  display: flex;
  gap: 1.1rem;
  align-items: center;
}
.site-header nav a {
  color: var(--fg-muted);
  text-decoration: none;
  font-size: 0.92rem;
  font-weight: 500;
}
.site-header nav a:hover { color: var(--accent); }
#theme-toggle {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--fg);
  border-radius: 6px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 0.95rem;
}
#theme-toggle:hover { border-color: var(--accent); }

.article {
  padding: 3rem 1.25rem 5rem;
}

.article h1 {
  font-size: clamp(1.9rem, 4vw, 2.6rem);
  line-height: 1.2;
  letter-spacing: -0.02em;
  margin: 0 0 1rem;
  font-weight: 800;
}
.article h2 {
  font-size: 1.55rem;
  margin: 3rem 0 1rem;
  letter-spacing: -0.01em;
  font-weight: 700;
  border-top: 1px solid var(--border);
  padding-top: 2.5rem;
}
.article h3 {
  font-size: 1.2rem;
  margin: 2rem 0 0.6rem;
  font-weight: 700;
}

.article p { margin: 0 0 1.1rem; }
.article a { color: var(--accent); }
.article a:hover { text-decoration: underline; }

.article hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2.5rem 0;
}

.article ul, .article ol {
  padding-left: 1.4rem;
  margin: 0 0 1.2rem;
}
.article li { margin: 0.3rem 0; }

.article blockquote {
  margin: 1.5rem 0;
  padding: 0.9rem 1.2rem;
  border-left: 3px solid var(--accent);
  background: var(--bg-elev);
  border-radius: 0 8px 8px 0;
  color: var(--fg);
}
.article blockquote p:last-child { margin-bottom: 0; }

.article code {
  font-family: var(--font-mono);
  font-size: 0.88em;
  background: var(--code-bg);
  padding: 0.15em 0.4em;
  border-radius: 4px;
}
.article pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem 1.1rem;
  overflow-x: auto;
  font-size: 0.88rem;
  line-height: 1.55;
}
.article pre code {
  background: none;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

.article table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  font-size: 0.95rem;
}
.article th, .article td {
  border-bottom: 1px solid var(--border);
  padding: 0.65rem 0.8rem;
  text-align: left;
  vertical-align: top;
}
.article th {
  background: var(--bg-elev);
  font-weight: 600;
}
.article tr:hover td { background: var(--bg-elev); }

.article img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 2rem auto;
  background: white;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
}
[data-theme="dark"] .article img {
  filter: invert(0.92) hue-rotate(180deg);
  background: #f7f5f0;
}

.article ul li.task {
  list-style: none;
  margin-left: -1.2rem;
}
.article li.task input[type="checkbox"] {
  margin-right: 0.6rem;
  transform: translateY(2px);
  accent-color: var(--accent);
}

.katex-display {
  margin: 1.4rem 0;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.4rem 0;
}

.site-footer {
  border-top: 1px solid var(--border);
  padding: 2rem 0;
  color: var(--fg-muted);
  font-size: 0.88rem;
  text-align: center;
}
.site-footer a { color: var(--fg-muted); }
.site-footer a:hover { color: var(--accent); }

@media (max-width: 600px) {
  html, body { font-size: 16px; }
  .site-header nav a:not(:last-child) { display: none; }
  .article { padding-top: 2rem; }
}
"""


SCRIPT_JS = """(function () {
  var KEY = "hmd-theme";
  var btn = document.getElementById("theme-toggle");
  var root = document.documentElement;
  function apply(theme) {
    if (theme === "dark") root.setAttribute("data-theme", "dark");
    else root.removeAttribute("data-theme");
  }
  var saved = localStorage.getItem(KEY);
  if (saved) apply(saved);
  else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) apply("dark");
  btn && btn.addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    apply(next);
    localStorage.setItem(KEY, next);
  });
})();
"""


def build() -> None:
    body = render_readme()
    html = PAGE_TEMPLATE.format(
        title=SITE_TITLE,
        description=SITE_DESCRIPTION,
        repo_url=REPO_URL,
        body=body,
    )

    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    (DOCS / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (DOCS / "script.js").write_text(SCRIPT_JS, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    charts_dst = DOCS / "charts"
    if charts_dst.exists():
        shutil.rmtree(charts_dst)
    shutil.copytree(CHARTS_SRC, charts_dst)

    print(f"Built {DOCS}/")
    for p in sorted(DOCS.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(ROOT)}  ({p.stat().st_size:,} B)")


if __name__ == "__main__":
    build()
