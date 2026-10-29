#!/usr/bin/env python3
"""Project health check. Run from the repo root:  python3 scripts/check.py

1. Builds the site with Hugo and fails on any WARN or ERROR.
2. Confirms the expected pages exist, and that the content blocks
   (servicios/, proyectos/, nosotros/, contacto) did not become pages.
3. Checks that every internal link (href, src, CSS url()) resolves to a file
   in the build, with the site served from a subpath like /gps-electronics/.

Needs: hugo (extended, >= 0.166). Standard library only.
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlsplit

# Subpath build, to catch root-absolute links.
BASE = "http://localhost/gps-electronics/"
PAGES = ["index.html", "404.html", "sitemap.xml", "robots.txt"]
BLOCKS = ["servicios", "proyectos", "nosotros", "contacto"]
problems = []


def fail(msg):
    problems.append(msg)


# 1. Build -------------------------------------------------------------------
out = tempfile.mkdtemp(prefix="gps-build-")
res = subprocess.run(
    ["hugo", "--gc", "--minify", "--baseURL", BASE, "--destination", out],
    capture_output=True, text=True,
)
log = res.stdout + res.stderr
for line in log.splitlines():
    if line.startswith(("WARN", "ERROR")):
        fail(f"hugo: {line}")
if res.returncode != 0:
    fail("hugo build failed")
    print(log)

# 2. Pages -------------------------------------------------------------------
for rel in PAGES:
    if not os.path.isfile(f"{out}/{rel}"):
        fail(f"missing: /{rel}")
for block in BLOCKS:
    if os.path.exists(f"{out}/{block}"):
        fail(f"content block rendered as a page: /{block}/")

# 3. Internal links ----------------------------------------------------------
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links += [v for k, v in attrs if k in ("href", "src") and v]


def page_url(path):
    rel = os.path.relpath(path, out).replace(os.sep, "/")
    return BASE + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)


def check_link(src, link):
    """Checks one link; returns True if it points at the site itself."""
    if link.startswith("#") or link.split(":", 1)[0] in ("mailto", "tel", "data"):
        return False
    url = urlsplit(urljoin(page_url(src), link))
    if url.scheme not in ("http", "https") or url.netloc != urlsplit(BASE).netloc:
        return False  # external
    base_path = urlsplit(BASE).path
    if not url.path.startswith(base_path):
        fail(f"{page_url(src)}: link '{link}' points outside {base_path}")
        return True
    target = os.path.join(out, unquote(url.path[len(base_path):]))
    if url.path.endswith("/") or os.path.isdir(target):
        target = os.path.join(target, "index.html")
    if not os.path.isfile(target):
        fail(f"{page_url(src)}: broken link '{link}'")
    return True


n_links = 0
for f in glob.glob(f"{out}/**/*.html", recursive=True):
    parser = LinkParser()
    parser.feed(open(f, encoding="utf-8").read())
    n_links += sum(check_link(f, link) for link in parser.links)
for f in glob.glob(f"{out}/**/*.css", recursive=True):
    css = open(f, encoding="utf-8").read()
    n_links += sum(check_link(f, link) for link in re.findall(r"url\(\s*['\"]?([^'\")]+)", css))

shutil.rmtree(out, ignore_errors=True)

if problems:
    print("✗ check failed:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print(f"✓ all good: build clean, {len(PAGES)} pages, no block pages, {n_links} internal links")
