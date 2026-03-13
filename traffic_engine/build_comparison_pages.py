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
    if not tools_path.exists():
        raise FileNotFoundError("tools.json not found")
    with tools_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_comparisons():
    comp_path = project_root() / "data" / "comparisons.json"
    if not comp_path.exists():
        return []
    with comp_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_comparison(comp, tools_by_slug):
    required = ["slug", "tool_a_slug", "tool_b_slug"]
    missing = [k for k in required if k not in comp]
    if missing:
        return False, f"Missing keys: {', '.join(missing)}"
    if comp["tool_a_slug"] not in tools_by_slug:
        return False, f"Tool A slug '{comp['tool_a_slug']}' not found"
    if comp["tool_b_slug"] not in tools_by_slug:
        return False, f"Tool B slug '{comp['tool_b_slug']}' not found"
    if comp["tool_a_slug"] == comp["tool_b_slug"]:
        return False, "Cannot compare a tool to itself"
    return True, ""


def get_tool_by_slug(tools_list, slug):
    for t in tools_list:
        if t["slug"] == slug:
            return t
    return None


def build_tool_highlights(tool):
    price = tool.get("monthly_price", 0)
    hours = tool.get("default_hours_saved", 0)
    summary = tool.get("short_summary", "AI productivity tool")
    items = [
        f"${price}/month",
        f"~{hours} hrs/week reported savings",
        summary[:120].rstrip(".") + ".",
    ]
    return "\n".join(f"<li>{html.escape(i)}</li>" for i in items)


def build_related_links(tools_list, tool_a_slug, tool_b_slug):
    related = []
    for tool in tools_list:
        if tool["slug"] in (tool_a_slug, tool_b_slug):
            continue
        href = internal_url(f"/tools/{tool['slug']}-worth-it-calculator/")
        related.append(f'<li><a href="{href}">{html.escape(tool["name"])} Calculator</a></li>')
        if len(related) >= 4:
            break
    return "\n".join(related)


def render_comparison_page(comp, tools_list, template):
    now = datetime.date.today()
    last_updated = now.strftime("%B %Y")

    tool_a = get_tool_by_slug(tools_list, comp["tool_a_slug"])
    tool_b = get_tool_by_slug(tools_list, comp["tool_b_slug"])

    if not tool_a or not tool_b:
        return None

    title = f"{tool_a['name']} vs {tool_b['name']} ({now.year}) – Which Saves More Time?"
    meta_description = (
        f"Head-to-head: {tool_a['name']} vs {tool_b['name']} — pricing, features, time savings, and which one fits your workflow better."
    )
    h1 = f"{tool_a['name']} vs {tool_b['name']}"

    intro = comp.get("intro", "Comparing two strong AI productivity tools side by side.")
    verdict = comp.get("verdict", "Depends on your exact use case — run both calculators to see real numbers.")
    best_for = comp.get("best_for", "Both can deliver value; the right choice depends on priorities.")
    when_to_choose = comp.get("when_to_choose", "Evaluate based on your workflow and run the calculators.")

    return template.format(
        title=html.escape(title),
        meta_description=html.escape(meta_description),
        h1=html.escape(h1),
        last_updated=last_updated,
        intro=html.escape(intro),
        tool_a_name=html.escape(tool_a["name"]),
        tool_b_name=html.escape(tool_b["name"]),
        tool_a_highlights=build_tool_highlights(tool_a),
        tool_b_highlights=build_tool_highlights(tool_b),
        tool_a_calculator_path=internal_url(f"/tools/{tool_a['slug']}-worth-it-calculator/"),
        tool_b_calculator_path=internal_url(f"/tools/{tool_b['slug']}-worth-it-calculator/"),
        tool_a_affiliate_link=html.escape(tool_a.get("affiliate_link", "#"), quote=True),
        tool_b_affiliate_link=html.escape(tool_b.get("affiliate_link", "#"), quote=True),
        verdict=html.escape(verdict),
        best_for=html.escape(best_for),
        when_to_choose=html.escape(when_to_choose),
        related_links=build_related_links(tools_list, comp["tool_a_slug"], comp["tool_b_slug"]),
        stylesheet_url=internal_url("/assets/styles.css"),
        home_url=internal_url("/"),
        tools_url=internal_url("/tools/"),
        about_url=internal_url("/about/"),
        methodology_url=internal_url("/methodology/"),
        contact_url=internal_url("/contact/"),
        privacy_url=internal_url("/privacy/"),
        disclosure_url=internal_url("/disclosure/"),
    )


def generate_sitemap(tools_list, comparisons):
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

    for comp in comparisons:
        urls.append(
            {
                "loc": absolute_url(f"/compare/{comp['slug']}/"),
                "lastmod": now,
                "priority": "0.75",
            }
        )

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        sitemap_lines.append("  <url>")
        sitemap_lines.append(f"    <loc>{html.escape(u['loc'])}</loc>")
        sitemap_lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        sitemap_lines.append(f"    <priority>{u['priority']}</priority>")
        sitemap_lines.append("  </url>")
    sitemap_lines.append("</urlset>")
    return "\n".join(sitemap_lines) + "\n"


def main():
    root = project_root()
    tools_list = load_tools()
    comparisons = load_comparisons()

    template_path = root / "templates" / "comparison_template.html"
    with template_path.open("r", encoding="utf-8") as f:
        template = f.read()

    compare_root = root / "compare"
    compare_root.mkdir(parents=True, exist_ok=True)

    tools_by_slug = {t["slug"]: t for t in tools_list}

    generated = 0
    skipped = 0

    for comp in comparisons:
        valid, error = validate_comparison(comp, tools_by_slug)
        if not valid:
            print(f"Skipped invalid comparison '{comp.get('slug', 'unknown')}': {error}")
            skipped += 1
            continue

        content = render_comparison_page(comp, tools_list, template)
        if content is None:
            print(f"Failed to render comparison '{comp['slug']}': tools missing")
            skipped += 1
            continue

        page_dir = compare_root / comp["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(content, encoding="utf-8")
        generated += 1

    (root / "sitemap.xml").write_text(generate_sitemap(tools_list, comparisons), encoding="utf-8")

    print(f"Generated {generated} comparison pages")
    print(f"Skipped {skipped} invalid comparisons")


if __name__ == "__main__":
    main()