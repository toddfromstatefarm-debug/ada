# AI Productivity Calculator Library

Zero-cost static site that generates “Is this tool worth it?” calculator pages from one JSON file.

## Structure
- `data/tools.json` — tool data
- `templates/calculator.html` — calculator page template
- `scripts/generate_pages.py` — local generator
- `tools/` — generated hub and calculator pages
- `index.html` — generated homepage
- `sitemap.xml` — generated sitemap

## Run
From the project root:

```bash
python scripts/generate_pages.py
```

## Deploy
Push the generated files to GitHub Pages or Cloudflare Pages, then submit `sitemap.xml` in Google Search Console.
