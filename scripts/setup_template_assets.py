"""
scripts/setup_template_assets.py
Distributes required LaTeX class files (.cls) to template directories.
"""
import urllib.request
import ssl
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "resume_templates"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0"}

cls_sources = {
    "awesome-cv.cls": "https://raw.githubusercontent.com/posquit0/Awesome-CV/master/awesome-cv.cls",
    "altacv.cls": "https://raw.githubusercontent.com/liantze/AltaCV/main/altacv.cls",
    "deedy-resume-openfont.cls": "https://raw.githubusercontent.com/deedy/Deedy-Resume/master/OpenFonts/deedy-resume-openfont.cls",
    "resume.cls": "https://raw.githubusercontent.com/Elijas/latex-resume-template/master/resume.cls",
    "friggeri-cv.cls": "https://raw.githubusercontent.com/martinbjeldbak/afriggeri-cv/master/friggeri-cv.cls",
}

downloaded = {}
for name, url in cls_sources.items():
    print(f"Downloading {name} from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            downloaded[name] = r.read()
            print(f"  -> {name}: {len(downloaded[name])} bytes")
    except Exception as e:
        print(f"  -> Error downloading {name}: {e}")

# Mapping templates to their class files
mapping = {
    "awesome-cv": [("awesome-cv.cls", "awesome-cv.cls")],
    "altacv": [("altacv.cls", "altacv.cls")],
    "altacv-lightdark": [("altacv.cls", "altacv.cls")],
    "altacv-editorial": [("altacv.cls", "altacv.cls")],
    "maltacv": [("altacv.cls", "altacv.cls")],
    "deedy-cv": [("deedy-resume-openfont.cls", "deedy-resume-openfont.cls")],
    "deedy-modified": [("deedy-resume-openfont.cls", "deedy-resume-openfont.cls")],
    "deedy-single-column": [("deedy-resume-openfont.cls", "deedy-resume-openfont.cls")],
    "modern-deedy": [
        ("deedy-resume-openfont.cls", "deedy-resume-openfont.cls"),
        ("deedy-resume-openfont.cls", "resume-openfont.cls"),
    ],
    "faangpath-simple": [("resume.cls", "resume.cls")],
    "friggeri-cv": [
        ("friggeri-cv.cls", "friggeri-cv.cls"),
        ("friggeri-cv.cls", "cv-style.cls"),
    ],
    "friggeri-modified": [("friggeri-cv.cls", "friggeri-cv.cls")],
}

for slug, files in mapping.items():
    tdir = TEMPLATES_DIR / slug
    if tdir.exists():
        for src_key, dest_name in files:
            if src_key in downloaded:
                (tdir / dest_name).write_bytes(downloaded[src_key])
                print(f"Copied {dest_name} to {slug}")

print("Assets distribution complete!")
