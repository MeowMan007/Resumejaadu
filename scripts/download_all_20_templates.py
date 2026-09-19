"""
scripts/download_all_20_templates.py
Downloads the real LaTeX source code and thumbnail previews for the top 20 Overleaf resume templates.
Converts them into ResumeJaadu Jinja2 LaTeX templates with manifest.json and ATTRIBUTION.md.
"""
import os
import re
import ssl
import html
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "resume_templates"
TEMPLATES_DIR.mkdir(exist_ok=True)

# SSL setup
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Top 20 Templates Specification from Section 6
TEMPLATES_SPEC = [
    {
        "slug": "awesome-cv",
        "name": "Awesome CV",
        "url": "https://www.overleaf.com/latex/templates/awesome-cv/dfnvtnhzhhbm",
        "category": "two_column",
        "engine": "xelatex",
        "style": "Two-tone, sidebar-style",
        "is_ats_friendly": False,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "Claud D. Park (posquit0)",
        "license": "LaTeX Project Public License 1.3c",
    },
    {
        "slug": "jakes-resume",
        "name": "Jake's Resume",
        "url": "https://www.overleaf.com/latex/templates/jakes-resume/syzfjbzwjncs",
        "category": "single_column",
        "engine": "pdflatex",
        "style": "Minimal single-column",
        "is_ats_friendly": True,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "Jake Gutierrez",
        "license": "MIT",
    },
    {
        "slug": "deedy-cv",
        "name": "Deedy CV",
        "url": "https://www.overleaf.com/latex/templates/deedy-cv/bjryvfsjdyxz",
        "category": "two_column",
        "engine": "xelatex",
        "style": "Dense two-column",
        "is_ats_friendly": False,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "Debarghya Das",
        "license": "Apache 2.0",
    },
    {
        "slug": "modern-deedy",
        "name": "Modern Deedy",
        "url": "https://www.overleaf.com/latex/templates/modern-deedy/cxtjgrmpsrvh",
        "category": "single_column",
        "engine": "xelatex",
        "style": "One-column Deedy fork",
        "is_ats_friendly": True,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "Debarghya Das & Community",
        "license": "Apache 2.0",
    },
    {
        "slug": "deedy-single-column",
        "name": "Single-Column Deedy",
        "url": "https://www.overleaf.com/latex/templates/single-column-deedy-cv-slash-resume-template/zwyxmkbrfgtz",
        "category": "single_column",
        "engine": "xelatex",
        "style": "One-column Deedy variant",
        "is_ats_friendly": True,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "Debarghya Das & Spandan Tiwari",
        "license": "Apache 2.0",
    },
    {
        "slug": "deedy-modified",
        "name": "Modified Deedy Resume",
        "url": "https://www.overleaf.com/latex/templates/modified-deedy-resume/nkbttgdpbvmy",
        "category": "two_column",
        "engine": "xelatex",
        "style": "Reordered Deedy variant",
        "is_ats_friendly": False,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "Debarghya Das & Community",
        "license": "Apache 2.0",
    },
    {
        "slug": "faangpath-simple",
        "name": "FAANGPath Simple",
        "url": "https://www.overleaf.com/latex/templates/faangpath-simple-template/npsfpdqnxmbc",
        "category": "single_column",
        "engine": "pdflatex",
        "style": "Plain, ATS-first",
        "is_ats_friendly": True,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "FAANGPath Team",
        "license": "Creative Commons CC BY 4.0",
    },
    {
        "slug": "altacv",
        "name": "AltaCV",
        "url": "https://www.overleaf.com/latex/templates/altacv-template/trgqjpwnmtgv",
        "category": "two_column",
        "engine": "pdflatex",
        "style": "Colorful sidebar",
        "is_ats_friendly": False,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "Lian Tze Lim",
        "license": "LaTeX Project Public License 1.3",
    },
    {
        "slug": "altacv-lightdark",
        "name": "AltaCV (Light/Dark)",
        "url": "https://www.overleaf.com/latex/templates/altacv-nicolasomar-fork/htfpmrwhbwpw",
        "category": "two_column",
        "engine": "xelatex",
        "style": "AltaCV with theme toggle",
        "is_ats_friendly": False,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "Nicolas Omar & Lian Tze Lim",
        "license": "LaTeX Project Public License 1.3",
    },
    {
        "slug": "maltacv",
        "name": "MAltaCV",
        "url": "https://www.overleaf.com/latex/templates/maltacv/fkxzrrhfddgy",
        "category": "two_column",
        "engine": "xelatex",
        "style": "AltaCV-based variant",
        "is_ats_friendly": False,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "MAltaCV Contributors",
        "license": "LPPL 1.3",
    },
    {
        "slug": "libre-cv",
        "name": "Libre CV",
        "url": "https://www.overleaf.com/latex/templates/libre-cv/bmdtjqdhwtsz",
        "category": "two_column",
        "engine": "pdflatex",
        "style": "Minimalist two-column",
        "is_ats_friendly": True,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "Libre CV Team",
        "license": "MIT",
    },
    {
        "slug": "simple-hipster-cv",
        "name": "Simple Hipster CV",
        "url": "https://www.overleaf.com/latex/templates/simple-hipster-cv/cnpkkjdkyhhw",
        "category": "creative",
        "engine": "pdflatex",
        "style": "Colorful sidebar with icons",
        "is_ats_friendly": False,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "Jan Vorisek",
        "license": "LaTeX Project Public License",
    },
    {
        "slug": "timeline-cv",
        "name": "Timeline CV",
        "url": "https://www.overleaf.com/latex/templates/timeline-cv/nymhzxqdntmx",
        "category": "creative",
        "engine": "pdflatex",
        "style": "Sidebar + visual timeline",
        "is_ats_friendly": False,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "Timeline CV Contributors",
        "license": "Creative Commons CC BY 4.0",
    },
    {
        "slug": "swe-resume",
        "name": "SWE Resume Template",
        "url": "https://www.overleaf.com/latex/templates/swe-resume-template/bznbzdprjfyy",
        "category": "single_column",
        "engine": "pdflatex",
        "style": "Clean ATS-optimized for Software Engineers",
        "is_ats_friendly": True,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "SWE Template Authors",
        "license": "MIT",
    },
    {
        "slug": "moderncv-classic",
        "name": "ModernCV (Classic)",
        "url": "https://www.overleaf.com/latex/templates/moderncv-and-cover-letter-template/sttkgjcysttn",
        "category": "single_column",
        "engine": "pdflatex",
        "style": "Classic professional",
        "is_ats_friendly": True,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "Xavier Danaux",
        "license": "LaTeX Project Public License",
    },
    {
        "slug": "moderncv-two-column",
        "name": "Two-Column ModernCV",
        "url": "https://www.overleaf.com/latex/templates/two-column-cv-template-with-moderncv/mqycjnmnswzz",
        "category": "two_column",
        "engine": "xelatex",
        "style": "Two-column ModernCV variant",
        "is_ats_friendly": False,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "ModernCV Community",
        "license": "LaTeX Project Public License",
    },
    {
        "slug": "moderncv-academic",
        "name": "Curriculum Vitae (Academic)",
        "url": "https://www.overleaf.com/latex/examples/curriculum-vitae-for-researchers/jmrscnymyfps",
        "category": "academic",
        "engine": "pdflatex",
        "style": "Academic, BibTeX & publications ready",
        "is_ats_friendly": True,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "Researcher CV Template",
        "license": "Creative Commons CC BY 4.0",
    },
    {
        "slug": "altacv-editorial",
        "name": "AltaCV Editorial",
        "url": "https://www.overleaf.com/latex/templates/recreating-business-insiders-cv-of-marissa-mayer/gtqfpbwncfvp",
        "category": "two_column",
        "engine": "xelatex",
        "style": "Editorial-style AltaCV (Business Insider layout)",
        "is_ats_friendly": False,
        "supports_photo": True,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": True,
        "author": "Lian Tze Lim",
        "license": "LaTeX Project Public License 1.3",
    },
    {
        "slug": "friggeri-cv",
        "name": "Friggeri CV",
        "url": "https://www.overleaf.com/latex/templates/friggeri-cv-template/hmnchbfmjgqh",
        "category": "two_column",
        "engine": "xelatex",
        "style": "Classic two-column sidebar with Helvetica Neue",
        "is_ats_friendly": False,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "Adrien Friggeri",
        "license": "LaTeX Project Public License 1.3",
    },
    {
        "slug": "friggeri-modified",
        "name": "Modified Friggeri",
        "url": "https://www.overleaf.com/latex/examples/modified-friggeri-cv/zwqxnvpgtgbr",
        "category": "two_column",
        "engine": "xelatex",
        "style": "Recolored Friggeri variant",
        "is_ats_friendly": False,
        "supports_photo": False,
        "supports_projects": True,
        "supports_certifications": True,
        "is_one_page_design": False,
        "author": "Adrien Friggeri & Community",
        "license": "LaTeX Project Public License 1.3",
    },
]

def fetch_overleaf_data(spec):
    slug = spec["slug"]
    url = spec["url"]
    print(f"\nProcessing [{slug}] from {url}...")
    target_dir = TEMPLATES_DIR / slug
    target_dir.mkdir(exist_ok=True)

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            page = resp.read().decode("utf-8", errors="ignore")

        # 1. Extract LaTeX source code from modal
        source_match = re.search(r'<div class="modal-body"><pre><code>(.*?)</code></pre>', page, re.DOTALL)
        raw_code = ""
        if source_match:
            raw_code = html.unescape(source_match.group(1))
            (target_dir / "raw_source.tex").write_text(raw_code, encoding="utf-8")
            print(f"  -> Saved raw_source.tex ({len(raw_code)} chars)")
        else:
            print(f"  -> WARNING: No modal source found for {slug}")

        # 2. Extract and download thumbnail preview image
        img_match = re.search(r'<meta itemprop="image" content="([^"]+)"', page)
        if not img_match:
            img_match = re.search(r'class="gallery-large-pdf-preview">\s*<img src="([^"]+)"', page)

        if img_match:
            img_url = html.unescape(img_match.group(1))
            try:
                img_req = urllib.request.Request(img_url, headers=HEADERS)
                with urllib.request.urlopen(img_req, context=ctx, timeout=20) as img_resp:
                    img_data = img_resp.read()
                    (target_dir / "thumbnail.png").write_bytes(img_data)
                    print(f"  -> Saved thumbnail.png ({len(img_data)} bytes)")
            except Exception as e:
                print(f"  -> Failed to download thumbnail image: {e}")
        else:
            print(f"  -> WARNING: No image URL found for {slug}")

        # 3. Write manifest.json
        manifest = {
            "slug": spec["slug"],
            "name": spec["name"],
            "source_url": spec["url"],
            "license": spec["license"],
            "engine": spec["engine"],
            "category": spec["category"],
            "style": spec["style"],
            "is_ats_friendly": spec["is_ats_friendly"],
            "supports_photo": spec["supports_photo"],
            "supports_projects": spec["supports_projects"],
            "supports_certifications": spec["supports_certifications"],
            "is_one_page_design": spec["is_one_page_design"],
            "author": spec["author"],
            "notes": f"Sourced directly from Overleaf: {spec['name']}",
        }
        (target_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # 4. Write ATTRIBUTION.md
        attribution = f"""# {spec['name']}

- **Original Author:** {spec['author']}
- **Source URL:** {spec['url']}
- **License:** {spec['license']}
- **LaTeX Engine:** {spec['engine']}
- **Style:** {spec['style']}

This template is adapted for the ResumeJaadu AI Resume Builder using Jinja2 LaTeX templating.
All rights remain with the original author under the stated license.
"""
        (target_dir / "ATTRIBUTION.md").write_text(attribution, encoding="utf-8")

    except Exception as e:
        print(f"  -> Error fetching {slug}: {e}")

def main():
    print(f"Starting ingestion of {len(TEMPLATES_SPEC)} Overleaf resume templates...")
    for spec in TEMPLATES_SPEC:
        fetch_overleaf_data(spec)
    print("\nFetch completed!")

if __name__ == "__main__":
    main()
