import json
import datetime
import html
from pathlib import Path

SITE_BASE_PATH = "/ada"
SITE_ROOT_URL = "https://toddfromstatefarm-debug.github.io/ada"


def internal_url(path: str) -> str:
    path = "/" + path.lstrip("/")
    return f"{SITE_BASE_PATH}{path}" if SITE_BASE_PATH else path


def absolute_url(path: str) -> str:
    path = "/" + path.lstrip("/")
    return f"{SITE_ROOT_URL}{path}"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_tools():
    tools_path = project_root() / "data" / "tools.json"
    with tools_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_template(template_name="calculator.html"):
    path = project_root() / "templates" / template_name
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def load_comparisons():
    comp_path = project_root() / "data" / "comparisons.json"
    if comp_path.exists():
        with comp_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_category_fallbacks(category: str):
    fallbacks = {
        "ai-scheduling": {
            "hours_saved_factors": [
                "manual calendar cleanup and rescheduling",
                "protecting focus / deep work time",
                "automatic habit scheduling",
                "smart buffer time around events"
            ],
            "conservative_hours": "1–2",
            "moderate_hours": "3–5",
            "aggressive_hours": "6–9",
        },
        "ai-meeting": {
            "hours_saved_factors": [
                "real-time note taking during calls",
                "writing post-meeting summaries & recaps",
                "extracting & tracking action items",
                "searching / referencing old meetings"
            ],
            "conservative_hours": "1–2",
            "moderate_hours": "2.5–5",
            "aggressive_hours": "6–10",
        },
        "ai-writing": {
            "hours_saved_factors": [
                "first-draft content generation",
                "rewriting / editing existing copy",
                "brainstorming and outlining",
                "creating multiple variants quickly"
            ],
            "conservative_hours": "1.5–3",
            "moderate_hours": "4–7",
            "aggressive_hours": "8–14",
        },
        "ai-productivity": {
            "hours_saved_factors": [
                "writing clearer tasks & descriptions",
                "summarizing updates & progress",
                "repetitive admin / project cleanup",
                "basic prioritization & grouping"
            ],
            "conservative_hours": "1–2",
            "moderate_hours": "3–5",
            "aggressive_hours": "6–10",
        },
    }
    return fallbacks.get(category, {
        "hours_saved_factors": ["repetitive workflow steps", "manual organization", "context switching", "recap & follow-up work"],
        "conservative_hours": "1–2",
        "moderate_hours": "3–5",
        "aggressive_hours": "6–10",
    })


def format_hours_saved_factors(factors):
    if not factors:
        return ""
    items = [f"<li>{html.escape(f)}</li>" for f in factors]
    return "<ul class=\"factors-list\">\n" + "\n".join(items) + "\n</ul>"


def build_related_tools(tools_list, current_tool):
    current_slug = current_tool["slug"]
    current_category = current_tool.get("category", "")
    same_category = sorted(
        [t for t in tools_list if t["slug"] != current_slug and t.get("category", "") == current_category],
        key=lambda t: t["name"].lower(),
    )
    related = same_category[:]
    if len(related) < 3:
        fallback = sorted(
            [t for t in tools_list if t["slug"] != current_slug and t["slug"] not in {r["slug"] for r in related}],
            key=lambda t: t["name"].lower(),
        )
        related.extend(fallback[:3 - len(related)])
    items = []
    for tool in related[:3]:
        name = html.escape(tool["name"])
        href = internal_url(f'/tools/{tool["slug"]}-worth-it-calculator/')
        items.append(f'<li><a href="{href}">{name} Calculator</a></li>')
    return "\n".join(items)


def site_shell_header() -> str:
    return (
        f'<header class="site-header"><div class="container header-inner">'
        f'<a class="brand" href="{internal_url("/")}">AI Productivity Calculators</a>'
        f'<nav class="site-nav">'
        f'<a href="{internal_url("/")}">Home</a>'
        f'<a href="{internal_url("/tools/")}">Tools</a>'
        f'<a href="{internal_url("/about/")}">About</a>'
        f'<a href="{internal_url("/methodology/")}">Methodology</a>'
        f'</nav></div></header>'
    )


def site_shell_footer() -> str:
    return (
        f'<footer class="site-footer"><div class="container"><ul class="footer-links">'
        f'<li><a href="{internal_url("/about/")}">About</a></li>'
        f'<li><a href="{internal_url("/contact/")}">Contact</a></li>'
        f'<li><a href="{internal_url("/privacy/")}">Privacy</a></li>'
        f'<li><a href="{internal_url("/disclosure/")}">Disclosure</a></li>'
        f'<li><a href="{internal_url("/methodology/")}">Methodology</a></li>'
        f'</ul><p class="small">© 2026 AI Productivity Calculators. All rights reserved.</p></div></footer>'
    )


def generate_calculator_page(tool, tools_list, template):
    now = datetime.date.today()
    last_updated = now.strftime("%B %Y")

    name = html.escape(tool["name"])
    monthly_price = tool.get("monthly_price", 0)
    default_hours = tool.get("default_hours_saved", 3)

    affiliate_link = html.escape(tool.get("affiliate_link", "#"), quote=True)

    calculator_intro   = html.escape(tool.get("calculator_intro",   f"{name} helps automate parts of your workflow. This calculator estimates whether the time saved justifies the monthly cost."))
    pricing_basis      = html.escape(tool.get("pricing_basis",       f"Uses the most common individual plan price (~${monthly_price}/mo). Check current official pricing."))
    interpretation_note = html.escape(tool.get("interpretation_note", "Positive results require consistent usage of the tool's core features. Low adoption = much lower real savings."))

    hourly_rate_guidance = html.escape(tool.get("hourly_rate_guidance", "Freelancers: use client billing rate. Salaried: salary ÷ 2080. If unsure, start conservative."))

    fb = get_category_fallbacks(tool.get("category", ""))
    conservative = tool.get("conservative_hours", fb["conservative_hours"])
    moderate     = tool.get("moderate_hours",     fb["moderate_hours"])
    aggressive   = tool.get("aggressive_hours",   fb["aggressive_hours"])

    factors_list = tool.get("hours_saved_factors", fb["hours_saved_factors"])
    factors_html = format_hours_saved_factors(factors_list)

    best_for    = html.escape(tool.get("best_for_override")    or "Professionals looking to save time in recurring workflows.")
    not_ideal   = html.escape(tool.get("not_ideal_for_override") or "Users with very light workloads or little need for this kind of automation.")

    return template.format(
        tool_name=name,
        monthly_price=monthly_price,
        default_hours_saved=default_hours,
        affiliate_link=affiliate_link,
        last_updated=last_updated,
        best_for=best_for,
        not_ideal_for=not_ideal,
        related_tools=build_related_tools(tools_list, tool),
        stylesheet_url=internal_url("/assets/styles.css"),
        home_url=internal_url("/"),
        tools_url=internal_url("/tools/"),
        about_url=internal_url("/about/"),
        methodology_url=internal_url("/methodology/"),
        contact_url=internal_url("/contact/"),
        privacy_url=internal_url("/privacy/"),
        disclosure_url=internal_url("/disclosure/"),
        calculator_intro=calculator_intro,
        pricing_basis=pricing_basis,
        hours_saved_factors=factors_html,
        conservative_hours=conservative,
        moderate_hours=moderate,
        aggressive_hours=aggressive,
        hourly_rate_guidance=hourly_rate_guidance,
        interpretation_note=interpretation_note,
    )


def generate_hub_page(tools_list):
    items = []
    for tool in sorted(tools_list, key=lambda t: t["name"].lower()):
        items.append(f'<li><a href="{internal_url(f"/tools/{tool["slug"]}-worth-it-calculator/")}">{html.escape(tool["name"])} Calculator</a></li>')
    joined = "\n      ".join(items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>All Tools - AI Productivity Calculators</title>
  <meta name="description" content="Browse all AI productivity tool calculators.">
  <link rel="stylesheet" href="{internal_url('/assets/styles.css')}">
</head>
<body>
  {site_shell_header()}
  <main class="container">
    <h1>All Calculators</h1>
    <p>Estimate whether each tool is worth the monthly cost for <em>your</em> workflow.</p>
    <ul class="tool-list">
      {joined}
    </ul>
  </main>
  {site_shell_footer()}
</body>
</html>
"""


def generate_homepage(tools_list, comparisons):
    featured_tools = sorted(tools_list, key=lambda t: t["name"].lower())[:6]
    featured_reviews = featured_tools[:4]
    featured_comparisons = comparisons[:4] if comparisons else []

    tool_items = "\n      ".join(
        f'<li><a href="{internal_url(f"/tools/{t["slug"]}-worth-it-calculator/")}">{html.escape(t["name"])} Calculator</a></li>'
        for t in featured_tools
    )
    review_items = "\n      ".join(
        f'<li><a href="{internal_url(f"/pages/{t["slug"]}-review/")}">{html.escape(t["name"])} Review</a></li>'
        for t in featured_reviews
    )
    comparison_items = "\n      ".join(
        f'<li><a href="{internal_url(f"/compare/{c["slug"]}/")}">{html.escape(c.get("title", c["slug"].replace("-", " ").title()))}</a></li>'
        for c in featured_comparisons
    ) if featured_comparisons else "<li>No comparisons added yet</li>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Productivity Calculators – Worth the Money?</title>
  <meta name="description" content="Free calculators that show whether popular AI productivity tools actually pay for themselves based on your hourly value and real usage.">
  <link rel="stylesheet" href="{internal_url('/assets/styles.css')}">
</head>
<body>
  {site_shell_header()}

  <main class="container">
    <section class="hero">
      <h1>Will this AI tool actually pay for itself in your week?</h1>
      <p>Run the numbers instead of trusting hype. Each calculator uses <strong>your</strong> hourly rate + realistic time-savings estimates to show net gain or loss — so you can decide with clarity instead of FOMO.</p>
    </section>

    <section class="card how-it-works">
      <h2>How It Works – 3 Steps</h2>
      <ol>
        <li>Enter your real hourly value (what an extra focused hour is actually worth to you).</li>
        <li>Estimate weekly hours saved — use conservative, moderate, or aggressive ranges provided.</li>
        <li>See instant monthly & annual net gain/loss + plain-English verdict.</li>
      </ol>
      <p><strong>Important:</strong> Results are only as good as your assumptions. Test multiple scenarios. Read the <a href="{internal_url('/methodology/')}">methodology</a> to understand how we calculate value.</p>
      <p class="small-note">Pricing references were checked recently, but software pricing changes fast. Always verify on the official site before subscribing.</p>
    </section>

    <section>
      <h2>Featured Calculators</h2>
      <ul class="featured-list">
        {tool_items}
      </ul>
      <p class="more-link"><a href="{internal_url('/tools/')}">See all tools →</a></p>
    </section>

    <section>
      <h2>Featured Reviews</h2>
      <ul class="featured-list">
        {review_items}
      </ul>
    </section>

    <section>
      <h2>Head-to-Head Comparisons</h2>
      <ul class="featured-list">
        {comparison_items}
      </ul>
    </section>

    <section class="card trust-callout">
      <h2>Why trust these calculators?</h2>
      <p>We focus on <em>your</em> time value — not generic hype. Every tool page includes realistic ranges, category-specific guidance, and clear warnings about when results overstate value. No magic multipliers. Just math + honest context.</p>
      <p><a href="{internal_url('/methodology/')}">Read full methodology →</a></p>
    </section>
  </main>

  {site_shell_footer()}
</body>
</html>
"""


def generate_sitemap(tools_list, comparisons):
    now = datetime.date.today().isoformat()
    urls = [
        {"loc": absolute_url("/"), "lastmod": now, "priority": "1.0"},
        {"loc": absolute_url("/tools/"), "lastmod": now, "priority": "0.9"},
    ]
    for tool in tools_list:
        urls.append({"loc": absolute_url(f'/tools/{tool["slug"]}-worth-it-calculator/'), "lastmod": now, "priority": "0.8"})
        urls.append({"loc": absolute_url(f'/pages/{tool["slug"]}-review/'), "lastmod": now, "priority": "0.7"})
    for comp in comparisons:
        urls.append({"loc": absolute_url(f'/compare/{comp["slug"]}/'), "lastmod": now, "priority": "0.75"})

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for entry in urls:
        sitemap.append("  <url>")
        sitemap.append(f'    <loc>{html.escape(entry["loc"])}</loc>')
        sitemap.append(f'    <lastmod>{entry["lastmod"]}</lastmod>')
        sitemap.append(f'    <priority>{entry["priority"]}</priority>')
        sitemap.append("  </url>")
    sitemap.append("</urlset>")
    return "\n".join(sitemap) + "\n"


def main():
    root = project_root()
    tools_list = load_tools()
    comparisons = load_comparisons()
    calc_template = load_template("calculator.html")

    valid_tools = []
    seen_slugs = set()
    for tool in tools_list:
        if "slug" not in tool or tool["slug"] in seen_slugs:
            print(f"Skipping invalid/duplicate tool: {tool.get('name', 'unknown')}")
            continue
        seen_slugs.add(tool["slug"])
        valid_tools.append(tool)

    tools_dir = root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    for tool in valid_tools:
        calc_dir = tools_dir / f'{tool["slug"]}-worth-it-calculator'
        calc_dir.mkdir(parents=True, exist_ok=True)
        content = generate_calculator_page(tool, valid_tools, calc_template)
        (calc_dir / "index.html").write_text(content, encoding="utf-8")

    (tools_dir / "index.html").write_text(generate_hub_page(valid_tools), encoding="utf-8")
    (root / "index.html").write_text(generate_homepage(valid_tools, comparisons), encoding="utf-8")
    (root / "sitemap.xml").write_text(generate_sitemap(valid_tools, comparisons), encoding="utf-8")

    print(f"Generated/updated {len(valid_tools)} calculator pages + homepage + hub + sitemap.")


if __name__ == "__main__":
    main()