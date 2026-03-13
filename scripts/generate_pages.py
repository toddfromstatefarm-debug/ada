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


def load_template():
    return (project_root() / "templates" / "calculator.html").read_text(encoding="utf-8")


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
    return copies.get(category, {
        "best_for": "Professionals looking to save time in recurring workflows.",
        "not_ideal_for": "Users with very light workloads or little need for automation.",
    })


def validate_tool(tool):
    required = ["name", "slug", "monthly_price", "default_hours_saved", "affiliate_link", "short_summary", "category"]
    for field in required:
        if field not in tool:
            return False, f"Missing field '{field}'"
        if isinstance(tool[field], str) and not tool[field].strip():
            return False, f"Empty field '{field}'"
    return True, ""


def build_related_tools(tools_list, current_tool):
    current_slug = current_tool["slug"]
    current_category = current_tool.get("category", "")
    same_category = sorted([t for t in tools_list if t["slug"] != current_slug and t.get("category", "") == current_category], key=lambda t: t["name"].lower())
    related = same_category[:]
    if len(related) < 3:
        fallback = sorted([t for t in tools_list if t["slug"] != current_slug and t["slug"] not in {r["slug"] for r in related}], key=lambda t: t["name"].lower())
        related.extend(fallback[: 3 - len(related)])
    return "\n".join(f'<li><a href="/tools/{tool["slug"]}-worth-it-calculator/">{html.escape(tool["name"])} Calculator</a></li>' for tool in related[:3])


def generate_calculator_page(tool, tools_list, template):
    now = datetime.date.today()
    copy = get_category_copy(tool.get("category", ""))
    return template.format(
        tool_name=html.escape(tool["name"]),
        monthly_price=tool.get("monthly_price", 0),
        default_hours_saved=tool.get("default_hours_saved", 0),
        affiliate_link=html.escape(tool.get("affiliate_link", "#"), quote=True),
        last_updated=now.strftime("%B %Y"),
        best_for=html.escape(tool.get("best_for_override") or copy["best_for"]),
        not_ideal_for=html.escape(tool.get("not_ideal_for_override") or copy["not_ideal_for"]),
        related_tools=build_related_tools(tools_list, tool),
    )


def generate_hub_page(tools_list):
    items = "".join(f'<li><a href="/tools/{tool["slug"]}-worth-it-calculator/">{html.escape(tool["name"])} </a></li>' for tool in sorted(tools_list, key=lambda t: t["name"].lower()))
    return f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>All Tools - AI Productivity Calculators</title><meta name="description" content="Browse all AI productivity calculators on the site."><link rel="stylesheet" href="/assets/styles.css"></head><body><header class="site-header"><div class="container header-inner"><a class="brand" href="/">AI Productivity Calculators</a><nav class="site-nav"><a href="/">Home</a><a href="/tools/">Tools</a><a href="/about/">About</a><a href="/methodology/">Methodology</a></nav></div></header><main class="container"><section class="hero"><h1>All Tools</h1><p>This library gathers every calculator on the site in one place. Use it to compare likely value across different categories of AI tools before you add another monthly subscription.</p></section><section class="card"><ul>{items}</ul></section></main><footer class="site-footer"><div class="container"><ul class="footer-links"><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/disclosure/">Disclosure</a></li><li><a href="/methodology/">Methodology</a></li></ul><p class="small">&copy; 2026 AI Productivity Calculators. All rights reserved.</p></div></footer></body></html>'


def generate_homepage(tools_list):
    featured = "".join(f'<li><a href="/tools/{tool["slug"]}-worth-it-calculator/">{html.escape(tool["name"])} </a></li>' for tool in tools_list[:5])
    return f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>AI Productivity Calculators</title><meta name="description" content="Free calculators and review pages to help decide whether AI productivity tools are worth the money."><link rel="stylesheet" href="/assets/styles.css"></head><body><header class="site-header"><div class="container header-inner"><a class="brand" href="/">AI Productivity Calculators</a><nav class="site-nav"><a href="/">Home</a><a href="/tools/">Tools</a><a href="/about/">About</a><a href="/methodology/">Methodology</a></nav></div></header><main class="container"><section class="hero"><h1>Decide if an AI tool actually pays for itself</h1><p>This site exists to answer one practical question: does the software save enough time to justify the monthly cost? Instead of vague hype, each page pushes the decision back to your hourly value, your workload, and your real usage.</p><p><a class="button" href="/methodology/">How the calculators work</a></p></section><div class="grid-two"><section class="card"><h2>What the site does</h2><p>Each calculator estimates your likely monthly gain or loss based on time saved, hourly value, and subscription price. Review pages add context so the numbers mean something in real life.</p></section><section class="card"><h2>Why it exists</h2><p>Too many software reviews quietly assume every tool is worth it. These pages are built to allow borderline or negative outcomes when the math does not support the subscription.</p></section></div><section class="card"><h2>Featured tools</h2><ul>{featured}</ul></section></main><footer class="site-footer"><div class="container"><ul class="footer-links"><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/disclosure/">Disclosure</a></li><li><a href="/methodology/">Methodology</a></li></ul><p class="small">&copy; 2026 AI Productivity Calculators. All rights reserved.</p></div></footer></body></html>'


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
    tools_list = [t for t in load_tools() if validate_tool(t)[0]]
    template = load_template()
    tools_dir = root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    for tool in tools_list:
        calc_dir = tools_dir / f'{tool["slug"]}-worth-it-calculator'
        calc_dir.mkdir(parents=True, exist_ok=True)
        (calc_dir / "index.html").write_text(generate_calculator_page(tool, tools_list, template), encoding="utf-8")
    (tools_dir / "index.html").write_text(generate_hub_page(tools_list), encoding="utf-8")
    (root / "index.html").write_text(generate_homepage(tools_list), encoding="utf-8")
    (root / "sitemap.xml").write_text(generate_sitemap(tools_list), encoding="utf-8")
    print(f"Generated {len(tools_list)} calculator pages.")

if __name__ == "__main__":
    main()
