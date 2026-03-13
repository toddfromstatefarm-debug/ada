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


def load_comparisons():
    comp_path = project_root() / "data" / "comparisons.json"
    with comp_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_comparison(comp, tools_by_slug):
    required = [
        "slug",
        "tool_a_slug",
        "tool_b_slug",
        "intro",
        "verdict",
        "best_for",
        "when_to_choose",
        "regret_risk",
        "overbuying_note",
    ]
    missing = [
        k for k in required
        if k not in comp or (isinstance(comp[k], str) and not comp[k].strip())
    ]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    if comp["tool_a_slug"] not in tools_by_slug:
        return False, f"Tool A '{comp['tool_a_slug']}' not found"
    if comp["tool_b_slug"] not in tools_by_slug:
        return False, f"Tool B '{comp['tool_b_slug']}' not found"
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
    summary_snip = summary[:120].rstrip(".") + "..."
    items = [
        f"${price}/mo baseline",
        f"~{hours} hrs/week reported savings",
        summary_snip,
    ]
    return "\n".join(f"<li>{html.escape(i)}</li>" for i in items)


def build_related_links(tools_list, tool_a_slug, tool_b_slug):
    related = []
    count = 0
    for tool in tools_list:
        if tool["slug"] in (tool_a_slug, tool_b_slug):
            continue
        slug = tool["slug"]
        name = html.escape(tool["name"])
        href = internal_url(f"/tools/{slug}-worth-it-calculator/")
        related.append(f'<li><a href="{href}">{name} Calculator</a></li>')
        count += 1
        if count >= 4:
            break
    return "\n".join(related)


def render_comparison_page(comp, tools_list, template):
    now = datetime.date.today()
    last_updated = now.strftime("%B %Y")

    tool_a = get_tool_by_slug(tools_list, comp["tool_a_slug"])
    tool_b = get_tool_by_slug(tools_list, comp["tool_b_slug"])

    if not tool_a or not tool_b:
        return None

    tool_a_slug = tool_a["slug"]
    tool_b_slug = tool_b["slug"]

    title = f"{tool_a['name']} vs {tool_b['name']} ({now.year}) – Which Actually Saves More Time?"
    meta_description = (
        f"Decisive {tool_a['name']} vs {tool_b['name']} comparison: pricing, "
        f"real workflow fit, time savings, regret risks, and who should pick which."
    )
    h1 = f"{tool_a['name']} vs {tool_b['name']}"

    return template.format(
        title=title,
        meta_description=meta_description,
        h1=h1,
        last_updated=last_updated,
        intro=html.escape(comp["intro"]),
        tool_a_name=html.escape(tool_a["name"]),
        tool_b_name=html.escape(tool_b["name"]),
        tool_a_highlights=build_tool_highlights(tool_a),
        tool_b_highlights=build_tool_highlights(tool_b),
        tool_a_calculator_path=internal_url(f"/tools/{tool_a_slug}-worth-it-calculator/"),
        tool_b_calculator_path=internal_url(f"/tools/{tool_b_slug}-worth-it-calculator/"),
        tool_a_affiliate_link=html.escape(tool_a.get("affiliate_link", "#"), quote=True),
        tool_b_affiliate_link=html.escape(tool_b.get("affiliate_link", "#"), quote=True),
        verdict=html.escape(comp["verdict"]),
        best_for=html.escape(comp["best_for"]),
        when_to_choose=html.escape(comp["when_to_choose"]),
        regret_risk=html.escape(comp["regret_risk"]),
        overbuying_note=html.escape(comp["overbuying_note"]),
        related_links=build_related_links(tools_list, comp["tool_a_slug"], comp["tool_b_slug"]),
        stylesheet_url=internal_url("/assets/styles.css"),
        home_url=internal_url("/"),
        tools_url=internal_url("/tools/"),
        about_url=internal_url("/about/"),
        contact_url=internal_url("/contact/"),
        privacy_url=internal_url("/privacy/"),
        methodology_url=internal_url("/methodology/"),
        disclosure_url=internal_url("/disclosure/"),
    )


def write_sitemap(tools_list, comparisons):
    now = datetime.date.today().isoformat()
    urls = [
        {"loc": absolute_url("/"), "lastmod": now, "priority": "1.0"},
        {"loc": absolute_url("/tools/"), "lastmod": now, "priority": "0.9"},
    ]

    for tool in tools_list:
        urls.append({
            "loc": absolute_url(f"/tools/{tool['slug']}-worth-it-calculator/"),
            "lastmod": now,
            "priority": "0.8",
        })

    for tool in tools_list:
        urls.append({
            "loc": absolute_url(f"/pages/{tool['slug']}-review/"),
            "lastmod": now,
            "priority": "0.7",
        })

    for comp in comparisons:
        urls.append({
            "loc": absolute_url(f"/compare/{comp['slug']}/"),
            "lastmod": now,
            "priority": "0.75",
        })

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

    sitemap_path = project_root() / "sitemap.xml"
    sitemap_path.write_text("\n".join(sitemap_lines) + "\n", encoding="utf-8")


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
            print(f"Failed to render '{comp['slug']}': tools missing")
            skipped += 1
            continue

        page_dir = compare_root / comp["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(content, encoding="utf-8")
        generated += 1

    write_sitemap(tools_list, comparisons)

    print(f"Generated {generated} comparison pages")
    print(f"Skipped {skipped} invalid comparisons")


if __name__ == "__main__":
    main()