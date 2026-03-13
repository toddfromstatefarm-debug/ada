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


def load_template():
    template_path = project_root() / "templates" / "calculator.html"
    with template_path.open("r", encoding="utf-8") as f:
        return f.read()


def load_comparisons():
    comp_path = project_root() / "data" / "comparisons.json"
    if comp_path.exists():
        with comp_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_category_copy(category: str):
    copies = {
        "ai-writing": {
            "best_for": "Content creators, bloggers, marketers, and anyone who writes regularly and wants faster drafting, editing, or outlining.",
            "not_ideal_for": "People with very light writing needs or users who want total manual control over every word.",
        },
        "ai-scheduling": {
            "best_for": "Busy freelancers, consultants, and operators juggling meetings, deep work, and calendar complexity.",
            "not_ideal_for": "People with simple schedules, minimal meetings, or a workflow that does not depend on calendar coordination.",
        },
        "ai-productivity": {
            "best_for": "Knowledge workers, project managers, and small teams trying to reduce repetitive admin and task overhead.",
            "not_ideal_for": "Users whose work is highly unstructured or who do not consistently use productivity systems.",
        },
        "ai-meeting": {
            "best_for": "Remote teams, client-facing professionals, and anyone who spends significant time in calls and follow-ups.",
            "not_ideal_for": "People who rarely join meetings or who do not need searchable notes and summaries.",
        },
    }
    return copies.get(
        category,
        {
            "best_for": "Professionals looking to save time in recurring workflows.",
            "not_ideal_for": "Users with very light workloads or little need for automation.",
        },
    )


def validate_tool(tool):
    required = [
        "name",
        "slug",
        "monthly_price",
        "default_hours_saved",
        "affiliate_link",
        "short_summary",
        "category",
    ]
    for field in required:
        if field not in tool:
            return False, f"Missing field '{field}'"
        if isinstance(tool[field], str) and not tool[field].strip():
            return False, f"Empty field '{field}'"
    if not isinstance(tool["name"], str):
        return False, "name must be a string"
    if not isinstance(tool["slug"], str):
        return False, "slug must be a string"
    if not isinstance(tool["monthly_price"], (int, float)) or tool["monthly_price"] < 0:
        return False, "monthly_price must be a non-negative number"
    if not isinstance(tool["default_hours_saved"], (int, float)) or tool["default_hours_saved"] < 0:
        return False, "default_hours_saved must be a non-negative number"
    if not str(tool["affiliate_link"]).startswith(("http://", "https://")):
        return False, "affiliate_link must be a valid URL"
    if not isinstance(tool["category"], str):
        return False, "category must be a string"
    return True, ""


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
        related.extend(fallback[: 3 - len(related)])
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
        f'</ul><p class="small">&copy; 2026 AI Productivity Calculators. All rights reserved.</p></div></footer>'
    )


def generate_calculator_page(tool, tools_list, template):
    now = datetime.date.today()
    last_updated = now.strftime("%B %Y")
    name = html.escape(tool["name"])
    monthly_price = tool.get("monthly_price", 0)
    default_hours_saved = tool.get("default_hours_saved", 0)
    affiliate_link = html.escape(tool.get("affiliate_link", "#"), quote=True)
    category = tool.get("category", "")
    copy = get_category_copy(category)
    best_for = html.escape(tool.get("best_for_override") or copy["best_for"])
    not_ideal_for = html.escape(tool.get("not_ideal_for_override") or copy["not_ideal_for"])
    return template.format(
        tool_name=name,
        monthly_price=monthly_price,
        default_hours_saved=default_hours_saved,
        affiliate_link=affiliate_link,
        last_updated=last_updated,
        best_for=best_for,
        not_ideal_for=not_ideal_for,
        related_tools=build_related_tools(tools_list, tool),
        stylesheet_url=internal_url("/assets/styles.css"),
        home_url=internal_url("/"),
        tools_url=internal_url("/tools/"),
        about_url=internal_url("/about/"),
        methodology_url=internal_url("/methodology/"),
        contact_url=internal_url("/contact/"),
        privacy_url=internal_url("/privacy/"),
        disclosure_url=internal_url("/disclosure/"),
    )


def generate_hub_page(tools_list):
    items = []
    for tool in sorted(tools_list, key=lambda t: t["name"].lower()):
        items.append(f'<li><a href="{internal_url(f"/tools/{tool["slug"]}-worth-it-calculator/")}">{html.escape(tool["name"])} Calculator</a></li>')
    joined = "\n      ".join(items)
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>All Tools - AI Productivity Calculators</title>
  <meta name=\"description\" content=\"Browse all AI productivity calculators on the site.\">
  <link rel=\"stylesheet\" href=\"{internal_url('/assets/styles.css')}\">
</head>
<body>
  {site_shell_header()}
  <main class=\"container\">
    <h1>All Tools</h1>
    <p>Browse every calculator on the site and quickly estimate whether a given tool is worth the monthly cost for your workflow.</p>
    <ul>
      {joined}
    </ul>
  </main>
  {site_shell_footer()}
</body>
</html>
"""


def generate_homepage(tools_list, comparisons):
    featured_tools = tools_list[:5]
    featured_reviews = tools_list[:5]
    featured_comparisons = comparisons[:5]
    tool_items = "\n      ".join(
        f'<li><a href="{internal_url(f"/tools/{t["slug"]}-worth-it-calculator/")}">{html.escape(t["name"])} Calculator</a></li>'
        for t in featured_tools
    )
    review_items = "\n      ".join(
        f'<li><a href="{internal_url(f"/pages/{t["slug"]}-review/")}">{html.escape(t["name"])} Review</a></li>'
        for t in featured_reviews
    )
    comparison_items = "\n      ".join(
        f'<li><a href="{internal_url(f"/compare/{c["slug"]}/")}">{html.escape(c["slug"].replace("-", " ").title())}</a></li>'
        for c in featured_comparisons
    )
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>AI Productivity Calculators</title>
  <meta name=\"description\" content=\"Free calculators, reviews, and comparisons to help you decide whether AI productivity tools are worth the money.\">
  <link rel=\"stylesheet\" href=\"{internal_url('/assets/styles.css')}\">
</head>
<body>
  {site_shell_header()}
  <main class=\"container\">
    <h1>Find Out If an AI Tool Actually Pays for Itself</h1>
    <p>This site helps freelancers, creators, and small teams estimate whether popular AI tools are actually worth the monthly cost.</p>

    <h2>How It Works</h2>
    <p>Each calculator combines a tool's current price with your own hourly value and estimated time savings. Instead of relying on hype, you can run the numbers for your real workflow.</p>
    <p><a href=\"{internal_url('/methodology/')}\">Read the methodology</a></p>

    <h2>Featured Calculators</h2>
    <ul>
      {tool_items}
    </ul>

    <h2>Featured Reviews</h2>
    <ul>
      {review_items}
    </ul>

    <h2>Featured Comparisons</h2>
    <ul>
      {comparison_items}
    </ul>
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
    template = load_template()

    valid_tools = []
    seen_slugs = set()
    for tool in tools_list:
        valid, error = validate_tool(tool)
        if not valid:
            print(f"Skipped invalid tool '{tool.get('name', 'unknown')}': {error}")
            continue
        if tool["slug"] in seen_slugs:
            print(f"Skipped duplicate slug '{tool['slug']}'")
            continue
        seen_slugs.add(tool["slug"])
        valid_tools.append(tool)

    tools_dir = root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    for tool in valid_tools:
        calc_dir = tools_dir / f'{tool["slug"]}-worth-it-calculator'
        calc_dir.mkdir(parents=True, exist_ok=True)
        content = generate_calculator_page(tool, valid_tools, template)
        (calc_dir / "index.html").write_text(content, encoding="utf-8")

    (tools_dir / "index.html").write_text(generate_hub_page(valid_tools), encoding="utf-8")
    (root / "index.html").write_text(generate_homepage(valid_tools, comparisons), encoding="utf-8")
    (root / "sitemap.xml").write_text(generate_sitemap(valid_tools, comparisons), encoding="utf-8")
    print(f"Generated {len(valid_tools)} calculator pages.")


if __name__ == "__main__":
    main()
