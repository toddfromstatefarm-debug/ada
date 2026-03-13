import json
import datetime
import html
from pathlib import Path

ROOT_URL = "https://aiproductivitycalculators.com"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_tools():
    tools_path = project_root() / "data" / "tools.json"
    with tools_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_comparisons():
    comp_path = project_root() / "data" / "comparisons.json"
    with comp_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_comparison(comp, tools_by_slug):
    required = ["slug", "tool_a_slug", "tool_b_slug", "intro", "verdict", "best_for", "when_to_choose"]
    missing = [k for k in required if k not in comp or (isinstance(comp[k], str) and not comp[k].strip())]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    if comp["tool_a_slug"] not in tools_by_slug:
        return False, f"Tool A slug '{comp['tool_a_slug']}' not found"
    if comp["tool_b_slug"] not in tools_by_slug:
        return False, f"Tool B slug '{comp['tool_b_slug']}' not found"
    if comp["tool_a_slug"] == comp["tool_b_slug"]:
        return False, "Cannot compare a tool to itself"
    return True, ""


def get_tool_by_slug(tools_list, slug):
    for tool in tools_list:
        if tool["slug"] == slug:
            return tool
    return None


def render_list_items(items):
    return "\n".join(f"<li>{html.escape(item)}</li>" for item in items)


def build_tool_highlights(tool):
    price = tool.get("monthly_price", 0)
    hours = tool.get("default_hours_saved", 0)
    features = tool.get("features", [])[:2]
    items = [
        f"${price}/month",
        f"About {hours} hours/week of reported savings",
    ]
    items.extend(features)
    return render_list_items(items)


def build_related_links(tools_list, tool_a_slug, tool_b_slug):
    related = []
    for tool in sorted(tools_list, key=lambda t: t["name"].lower()):
        if tool["slug"] in (tool_a_slug, tool_b_slug):
            continue
        related.append(f'<li><a href="/tools/{tool["slug"]}-worth-it-calculator/">{html.escape(tool["name"])} Calculator</a></li>')
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
    meta_description = f"Head-to-head: {tool_a['name']} vs {tool_b['name']} — pricing, features, time savings, and which one fits your workflow better."
    return template.format(
        title=html.escape(title),
        meta_description=html.escape(meta_description, quote=True),
        h1=html.escape(f"{tool_a['name']} vs {tool_b['name']}"),
        last_updated=last_updated,
        intro=html.escape(comp["intro"]),
        tool_a_name=html.escape(tool_a["name"]),
        tool_b_name=html.escape(tool_b["name"]),
        tool_a_highlights=build_tool_highlights(tool_a),
        tool_b_highlights=build_tool_highlights(tool_b),
        tool_a_calculator_path=f"/tools/{tool_a['slug']}-worth-it-calculator/",
        tool_b_calculator_path=f"/tools/{tool_b['slug']}-worth-it-calculator/",
        tool_a_affiliate_link=html.escape(tool_a.get("affiliate_link", "#"), quote=True),
        tool_b_affiliate_link=html.escape(tool_b.get("affiliate_link", "#"), quote=True),
        verdict=html.escape(comp["verdict"]),
        best_for=html.escape(comp["best_for"]),
        when_to_choose=html.escape(comp["when_to_choose"]),
        related_links=build_related_links(tools_list, comp["tool_a_slug"], comp["tool_b_slug"]),
    )


def write_sitemap(tools_list, comparisons):
    now = datetime.date.today().isoformat()
    urls = [
        {"loc": f"{ROOT_URL}/", "lastmod": now, "priority": "1.0"},
        {"loc": f"{ROOT_URL}/tools/", "lastmod": now, "priority": "0.9"},
    ]
    for tool in tools_list:
        urls.append({"loc": f"{ROOT_URL}/tools/{tool['slug']}-worth-it-calculator/", "lastmod": now, "priority": "0.8"})
    for tool in tools_list:
        urls.append({"loc": f"{ROOT_URL}/pages/{tool['slug']}-review/", "lastmod": now, "priority": "0.7"})
    for comp in comparisons:
        urls.append({"loc": f"{ROOT_URL}/compare/{comp['slug']}/", "lastmod": now, "priority": "0.75"})
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{html.escape(u['loc'])}</loc>")
        lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        lines.append(f"    <priority>{u['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (project_root() / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    root = project_root()
    tools_list = load_tools()
    comparisons = load_comparisons()
    tools_by_slug = {t["slug"]: t for t in tools_list}
    template = (root / "templates" / "comparison_template.html").read_text(encoding="utf-8")
    compare_root = root / "compare"
    compare_root.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0
    valid_comparisons = []
    for comp in comparisons:
        valid, error = validate_comparison(comp, tools_by_slug)
        if not valid:
            print(f"Skipped invalid comparison '{comp.get('slug', 'unknown')}': {error}")
            skipped += 1
            continue
        content = render_comparison_page(comp, tools_list, template)
        if content is None:
            skipped += 1
            continue
        page_dir = compare_root / comp["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(content, encoding="utf-8")
        generated += 1
        valid_comparisons.append(comp)

    write_sitemap(tools_list, valid_comparisons)
    print(f"Generated {generated} comparison pages")
    print(f"Skipped {skipped} invalid comparisons")


if __name__ == "__main__":
    main()
