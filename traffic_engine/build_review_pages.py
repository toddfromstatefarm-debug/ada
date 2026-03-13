import json
import datetime
import html
from pathlib import Path

ROOT_URL = "https://aiproductivitycalculators.com"

def project_root() -> Path:
    return Path(__file__).resolve().parent.parent

def load_tools():
    with (project_root() / "data" / "tools.json").open("r", encoding="utf-8") as f:
        return json.load(f)

def validate_tool(tool):
    required = ["name", "slug", "category"]
    for field in required:
        if field not in tool:
            return False, f"Missing keys: {field}"
    return True, ""

def get_category_copy(category):
    copies = {
        "ai-writing": {"best_for": "Content creators, bloggers, marketers, and anyone who writes regularly and wants faster drafting or editing.", "not_ideal_for": "People with very light writing needs or users who prefer fully manual writing workflows."},
        "ai-scheduling": {"best_for": "Busy freelancers, consultants, and operators managing meetings, deadlines, and deep work.", "not_ideal_for": "Users with simple schedules or very little calendar complexity."},
        "ai-productivity": {"best_for": "Knowledge workers, project managers, and small teams trying to reduce repetitive admin work.", "not_ideal_for": "Users who do not use task systems consistently or who need little automation."},
        "ai-meeting": {"best_for": "Remote teams, client-facing roles, and anyone who wants transcripts and summaries after calls.", "not_ideal_for": "People who rarely join meetings or do not need searchable notes."},
    }
    return copies.get(category, {"best_for": "Professionals looking to save time in recurring workflows.", "not_ideal_for": "Users with minimal repetitive work or low software budgets."})

def build_related_tools(tools_list, current_tool):
    current_slug = current_tool["slug"]
    current_category = current_tool.get("category", "")
    same_category = sorted([t for t in tools_list if t["slug"] != current_slug and t.get("category", "") == current_category], key=lambda t: t["name"].lower())
    related = same_category[:]
    if len(related) < 3:
        fallback = sorted([t for t in tools_list if t["slug"] != current_slug and t["slug"] not in {r["slug"] for r in related}], key=lambda t: t["name"].lower())
        related.extend(fallback[: 3 - len(related)])
    return "\n".join(f'<li><a href="/pages/{tool["slug"]}-review/">{html.escape(tool["name"])} Review</a></li>' for tool in related[:3])

def render_list_items(items):
    return "\n".join(f"<li>{html.escape(item)}</li>" for item in items)

def render_review_page(tool, tools_list, template):
    now = datetime.date.today()
    cat = get_category_copy(tool.get("category", ""))
    return template.format(
        title=f'{html.escape(tool["name"])} Review ({now.year}): Honest Analysis & ROI Check',
        meta_description=html.escape(f'Honest {tool["name"]} review covering features, pros, cons, pricing, and time-savings potential.', quote=True),
        h1=f'{html.escape(tool["name"])} Review',
        review_summary=html.escape(tool.get("review_summary", tool.get("short_summary", ""))),
        features=render_list_items(tool.get("features", ["AI-powered productivity enhancement"])),
        best_for=html.escape(tool.get("best_for_override") or cat["best_for"]),
        not_ideal_for=html.escape(tool.get("not_ideal_for_override") or cat["not_ideal_for"]),
        pros=render_list_items(tool.get("pros", ["May save time for active users", "Accessible price point", "Can fit well into workflows"])),
        cons=render_list_items(tool.get("cons", ["Requires setup and habit changes", "Recurring monthly cost", "Real value depends on usage"])),
        monthly_price=tool.get("monthly_price", 0),
        pricing_note=html.escape(tool.get("pricing_note", "Check the official site for current pricing and plan details.")),
        calculator_path=f'/tools/{tool["slug"]}-worth-it-calculator/',
        tool_name=html.escape(tool["name"]),
        affiliate_link=html.escape(tool.get("affiliate_link", "#"), quote=True),
        related_tools=build_related_tools(tools_list, tool),
        last_updated=now.strftime("%B %Y"),
    )

def generate_sitemap(tools_list):
    now = datetime.date.today().isoformat()
    urls = [{"loc": f"{ROOT_URL}/", "lastmod": now, "priority": "1.0"}, {"loc": f"{ROOT_URL}/tools/", "lastmod": now, "priority": "0.9"}]
    for tool in tools_list:
        urls.append({"loc": f'{ROOT_URL}/tools/{tool["slug"]}-worth-it-calculator/', "lastmod": now, "priority": "0.8"})
    for tool in tools_list:
        urls.append({"loc": f'{ROOT_URL}/pages/{tool["slug"]}-review/', "lastmod": now, "priority": "0.7"})
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for entry in urls:
        out.extend(["  <url>", f'    <loc>{html.escape(entry["loc"])}</loc>', f'    <lastmod>{entry["lastmod"]}</lastmod>', f'    <priority>{entry["priority"]}</priority>', "  </url>"])
    out.append("</urlset>")
    return "\n".join(out) + "\n"

def main():
    root = project_root()
    template = (root / "templates" / "review_template.html").read_text(encoding="utf-8")
    tools_list = [t for t in load_tools() if validate_tool(t)[0]]
    pages_dir = root / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    for tool in tools_list:
        review_dir = pages_dir / f'{tool["slug"]}-review'
        review_dir.mkdir(parents=True, exist_ok=True)
        (review_dir / "index.html").write_text(render_review_page(tool, tools_list, template), encoding="utf-8")
    (root / "sitemap.xml").write_text(generate_sitemap(tools_list), encoding="utf-8")
    print(f"Generated {len(tools_list)} review pages")

if __name__ == "__main__":
    main()
