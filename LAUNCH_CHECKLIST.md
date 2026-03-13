# AI Productivity Calculators – Launch Readiness Checklist
Date: March 2026

Before going live or submitting to Google:

### Domain & Hosting
- [ ] Purchase and connect the real domain
- [ ] Point domain to GitHub Pages or Cloudflare Pages
- [ ] Enable HTTPS
- [ ] Update ROOT_URL in all generator scripts to match the live domain

### Content & Trust Pages
- [ ] Replace placeholder email in /contact/ with your real address
- [ ] Review /about/, /methodology/, /disclosure/, and /privacy/ for final wording
- [ ] Confirm every page has visible disclosure language near affiliate CTAs
- [ ] Confirm footer links work on every page type

### Affiliate & Monetization
- [ ] Replace placeholder affiliate links in tools.json with real tracking links
- [ ] Verify each affiliate link redirects correctly
- [ ] Confirm disclosure language matches the affiliate programs you actually use

### Technical & SEO
- [ ] Run python scripts/generate_pages.py with no errors
- [ ] Run python traffic_engine/build_review_pages.py with no errors
- [ ] Run python traffic_engine/build_comparison_pages.py with no errors
- [ ] Open 10 random calculator, review, and comparison pages in a browser
- [ ] Confirm mobile rendering looks clean
- [ ] Confirm sitemap.xml contains homepage, hub, calculators, reviews, and comparisons
- [ ] Submit sitemap.xml in Google Search Console
- [ ] Request indexing for the homepage and a few key pages

### Final Manual Checks
- [ ] Test calculator JS on several pages
- [ ] Confirm verdict messages appear correctly
- [ ] Confirm no broken internal links remain
- [ ] Read homepage copy out loud and confirm it sounds human and trustworthy
- [ ] Remove any leftover placeholders before launch
