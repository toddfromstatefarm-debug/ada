iimport json
import os
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
    if not tools_path.exists():
        raise FileNotFoundError(f"tools.json not found at {tools_path}")
    with tools_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_tool(tool):
    required_keys = ["name", "slug", "category"]
    missing = [k for k in required_keys if k not in tool]
    if missing:
        return False, f"Missing keys: {', '.join(missing)}"
    if not isinstance(tool["name"], str) or not tool["name"].strip():
        return False, "Invalid name"
    if not isinstance(tool["slug"], str) or not tool["slug"].strip():
        return False, "Invalid slug"
    return True, ""


def get_category_copy(category):
    copies = {
        "ai-writing": {
            "best_for": "Content creators, bloggers, marketers, and anyone who writes regularly and wants faster drafting or editing.",
            "not_ideal_for": "People with very light writing needs or users who prefer fully manual writing workflows.",
        },
        "ai-scheduling": {
            "best_for": "Busy freelancers, consultants, and operators managing meetings, deadlines, and deep work.",
            "not_ideal_for": "Users with simple schedules or very little calendar complexity.",
        },
        "ai-productivity": {
            "best_for": "Knowledge workers, project managers, and small teams trying to reduce repetitive admin work.",
            "not_ideal_for": "Users who do not use task systems consistently or who need little automation.",
        },
        "ai-meeting": {
            "best_for": "Remote teams, client-facing roles, and anyone who wants transcripts and summaries after calls.",
            "not_ideal_for": "People who rarely join meetings or do not need searchable notes.",
        },
    }
    return copies.get(
        category,
        {
            "best_for": "Professionals looking to save time in recurring workflows.",
            "not_ideal_for": "Users with minimal repetitive work or low software budgets.",
        },
    )


def build_related_tools(tools_list, current_tool):
    current_slug = current_tool["slug"]
    current_category = current_tool.get("category", "")

    same_category = sorted(
        [
            t
            for t in tools_list
            if t["slug"] != current_slug and t.get("category", "") == current_category
        ],
        key=lambda t: t["name"].lower(),
    )

    related = same_category[:]

    if len(related) < 3:
        fallback = sorted(
            [
                t
                for t in tools_list
                if t["slug"] != current_slug and t["slug"] not in {r["slug"] for r in related}
            ],
            key=lambda t: t["name"].lower(),
        )
        related.extend(fallback[: 3 - len(related)])

    items = []
    for tool in related[:3]:
        name = html.escape(tool["name"])
        href = internal_url(f"/pages/{tool['slug']}-review/")
        items.append(f'<li><a href="{href}">{name} Review</a></li>')

    return "\n".join(items)


def render_list_items(items):
    return "\n".join(f"<li>{html.escape(item)}</li>" for item in items)


def render_review_page(tool, tools_list, template):
    now = datetime.date.today()
    last_updated = now.strftime("%B %Y")

    name = html.escape(tool["name"])
    monthly_price = tool.get("monthly_price", 0)
    affiliate_link = html.escape(tool.get("affiliate_link", "#"), quote=True)
    slug = tool["slug"]
    category = tool.get("category", "")

    title = f"{name} Review ({now.year}): Honest Analysis & ROI Check"
    meta_description = f"Honest {name} review covering features, pros, cons, pricing, and time-savings potential."
    h1 = f"{name} Review"

    review_summary = html.escape(
        tool.get("review_summary", tool.get("short_summary", f"{name} is an AI productivity tool."))
    )
    features = render_list_items(tool.get("features", ["AI-powered productivity enhancement"]))
    pros = render_list_items(
        tool.get("pros", ["May save time for active users", "Accessible price point", "Can fit well into workflows"])
    )
    cons = render_list_items(
        tool.get("cons", ["Requires setup and habit changes", "Recurring monthly cost", "Real value depends on usage"])
    )

    cat_copy = get_category_copy(category)
    best_for = html.escape(tool.get("best_for_override") or cat_copy["best_for"])
    not_ideal_for = html.escape(tool.get("not_ideal_for_override") or cat_copy["not_ideal_for"])
    pricing_note = html.escape(tool.get("pricing_note", "Check the official site for current pricing and plan details."))

    calculator_path = internal_url(f"/tools/{slug}-worth-it-calculator/")

    return template.format(
        title=title,
        meta_description=meta_description,
        h1=h1,
        review_summary=review_summary,
        features=features,
        best_for=best_for,
        not_ideal_for=not_ideal_for,
        pros=pros,
        cons=cons,
        monthly_price=monthly_price,
        pricing_note=pricing_note,
        calculator_path=calculator_path,
        tool_name=name,
        affiliate_link=affiliate_link,
        related_tools=build_related_tools(tools_list, tool),
        last_updated=last_updated,
        stylesheet_url=internal_url("/assets/styles.css"),
        home_url=internal_url("/"),
        tools_url=internal_url("/tools/"),
        about_url=internal_url("/about/"),
        methodology_url=internal_url("/methodology/"),
        contact_url=internal_url("/contact/"),
        privacy_url=internal_url("/privacy/"),
        disclosure_url=internal_url("/disclosure/"),
    )


def generate_sitemap(tools_list):
    now = datetime.date.today().isoformat()
    urls = [
        {"loc": absolute_url("/"), "lastmod": now, "priority": "1.0"},
        {"loc": absolute_url("/tools/"), "lastmod": now, "priority": "0.9"},
    ]

    for tool in tools_list:
        urls.append(
            {
                "loc": absolute_url(f"/tools/{tool['slug']}-worth-it-calculator/"),
                "lastmod": now,
                "priority": "0.8",
            }
        )

    for tool in tools_list:
        urls.append(
            {
                "loc": absolute_url(f"/pages/{tool['slug']}-review/"),
                "lastmod": now,
                "priority": "0.7",
            }
        )

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
    template_path = root / "templates" / "review_template.html"

    with template_path.open("r", encoding="utf-8") as f:
        template = f.read()

    tools_list = load_tools()
    valid_tools = []
    skipped = 0

    for tool in tools_list:
        valid, error = validate_tool(tool)
        if not valid:
            print(f"Skipped invalid tool '{tool.get('name', 'unknown')}': {error}")
            skipped += 1
            continue
        valid_tools.append(tool)

    pages_dir = root / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    for tool in valid_tools:
        review_dir = pages_dir / f"{tool['slug']}-review"
        review_dir.mkdir(parents=True, exist_ok=True)
        content = render_review_page(tool, valid_tools, template)
        (review_dir / "index.html").write_text(content, encoding="utf-8")

    (root / "sitemap.xml").write_text(generate_sitemap(valid_tools), encoding="utf-8")

    print(f"Generated {len(valid_tools)} review pages")
    print(f"Skipped {skipped} invalid tools")


if __name__ == "__main__":
    main()
