#!/usr/bin/env python3
"""Give Quarto's alias redirect stubs a crawlable <head>.

An `aliases:` entry in a page's front matter makes Quarto emit a stub at the old
URL that bounces to the new one. The stub it writes is JavaScript and nothing
else:

    <head>
      <title>Redirect</title>
      <script> ... window.location.replace(redirect) ... </script>
    </head>

Fine for a browser, close to useless for a crawler. There is no description — an
SEO audit reports the stub as a page missing one, which is what sent me here —
no canonical naming the destination, and no non-JS fallback, so anything that
does not run scripts sees an empty page titled "Redirect".

Run as a Quarto `post-render` step, this rewrites each stub in place to add:

  * <meta http-equiv="refresh" content="0; url=...">  a redirect crawlers honour
    without executing JS, and treat as equivalent to a 301.
  * <link rel="canonical" href="...">                 consolidates the old URL's
    signals onto the destination.
  * <meta name="description"> and a real <title>      lifted from the
    destination page, so the stub says where it is sending you.

The original <script> stays. It is the only part that preserves the #fragment,
which meta refresh cannot carry.

Deliberately no `noindex`: it contradicts a canonical — one says "index the
destination instead", the other "index nothing here" — and the guidance is not
to send both. Redirect plus canonical is the coherent pair.

It also repairs the redirect target. Quarto writes that target using the host's
path separator, so a render on Windows emits `..\\research\\index.html` into
what is meant to be a URL. Browsers paper over it (the URL parser folds `\\` to
`/` for http(s)), but it is not a valid relative URL and nothing else is obliged
to be so forgiving.

Stdlib only, and idempotent: a stub that already has a canonical is left alone,
so re-running over an unchanged docs/ is a no-op.

Run it by hand from the project root to check what it would do:

    python scripts/finish-alias-stubs.py
"""

from __future__ import annotations

import html
import json
import os
import posixpath
import re
import sys
from pathlib import Path


def plug_standard_streams() -> None:
    """Make file descriptors 0, 1 and 2 safe to hold open.

    Quarto's post-render step on Windows can start the script with stdout and
    stderr closed rather than inherited. That breaks this script in two ways,
    and the second is the nasty one:

      1. `print()` raises OSError EBADF.
      2. With fd 1 free, the *next* file opened is handed fd 1. Anything that
         later writes to stdout — the interpreter's own error reporting, say —
         writes into that file instead, and closing stdout at exit closes it out
         from under us. The observed symptom was EBADF raised from the open() in
         Path.write_text, before a single byte of HTML was written.

    Opening os.devnull over any missing descriptor closes the hole, so a file
    opened afterwards can never land on 0, 1 or 2.
    """
    for fd in (0, 1, 2):
        try:
            os.fstat(fd)
        except OSError:
            flags = os.O_RDONLY if fd == 0 else os.O_WRONLY
            spare = os.open(os.devnull, flags)
            if spare != fd:
                os.dup2(spare, fd)
                os.close(spare)

    # The Python-level objects can be None even once the descriptors are sound
    # (pythonw, and some subprocess launches).
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        try:
            if stream is None:
                raise OSError
            stream.fileno()
        except Exception:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))


plug_standard_streams()


def report(message: str) -> None:
    """Progress output that can never be the reason the build fails."""
    try:
        print(message, flush=True)
    except Exception:
        pass


# Quarto exports these for post-render scripts. The fallbacks let the script be
# run by hand from the project root, which is also how it gets tested.
OUTPUT_DIR = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "docs"))
PROJECT_DIR = Path(os.environ.get("QUARTO_PROJECT_DIR", "."))

REDIRECTS_RE = re.compile(r"var redirects = (\{.*?\});")
DESCRIPTION_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"')
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
SITEMAP_URL_RE = re.compile(r"[ \t]*<url>.*?</url>\n?", re.S)
LOC_RE = re.compile(r"<loc>([^<]*)</loc>")
ROBOTS_NOINDEX_RE = re.compile(r'<meta\s+name="robots"[^>]*content="[^"]*noindex', re.I)


def write_replacing(path: Path, text: str) -> None:
    """Write via a sibling temp file and an atomic rename.

    Truncating the real file in place would leave a half-written stub behind if
    the write failed — and on this project's OneDrive-backed working copy, a
    write failing is not hypothetical. os.replace is atomic on Windows and POSIX
    alike, so the stub is either the old one or the new one, never neither.
    """
    tmp = path.with_name(path.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def site_url() -> str:
    """Read `website.site-url` out of _quarto.yml.

    Parsed with a regex rather than PyYAML so the build keeps working on a
    machine where only the R toolchain was ever installed.
    """
    config = PROJECT_DIR / "_quarto.yml"
    match = re.search(
        r'^\s*site-url:\s*["\']?([^"\'\s#]+)', config.read_text(encoding="utf-8"), re.M
    )
    if not match:
        raise SystemExit(f"finish-alias-stubs: no `site-url` found in {config}")
    return match.group(1).rstrip("/")


def is_stub(text: str) -> bool:
    return "var redirects = " in text and "<title>Redirect</title>" in text


def target_of(text: str) -> str | None:
    """The stub's default destination, as a URL-shaped relative path."""
    match = REDIRECTS_RE.search(text)
    if not match:
        return None
    try:
        redirects = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    target = redirects.get("")
    # Windows separators, courtesy of a Windows render. See the module docstring.
    return target.replace("\\", "/") if target else None


def tidy_sitemap(base: str) -> None:
    """Make sitemap.xml agree with the canonicals, and drop noindex pages.

    Quarto writes every <loc> in `.../index.html` form while writing every
    <link rel="canonical"> in directory form, so each page is advertised under a
    URL its own canonical disowns. Google crawls the advertised one, reads the
    canonical, and files it under "Alternative page with proper canonical tag".
    A sitemap is meant to list canonical URLs, so the sitemap is the wrong half.

    It also lists /cv/, which carries a noindex meta tag — asking a crawler to
    fetch a page that then tells it not to index. Those come out entirely.

    Both URL forms keep working; this only changes which one is advertised.
    """
    sitemap = OUTPUT_DIR / "sitemap.xml"
    if not sitemap.is_file():
        return

    text = sitemap.read_text(encoding="utf-8")
    dropped = rewritten = 0

    def visit(match: re.Match[str]) -> str:
        nonlocal dropped, rewritten
        block = match.group(0)
        found = LOC_RE.search(block)
        if not found:
            return block
        loc = found.group(1)

        relative = loc[len(base) :].lstrip("/") if loc.startswith(base) else loc
        page = OUTPUT_DIR / (relative if relative else "index.html")
        if page.is_dir():
            page = page / "index.html"
        if page.is_file() and ROBOTS_NOINDEX_RE.search(page.read_text(encoding="utf-8")):
            dropped += 1
            return ""

        if loc.endswith("/index.html"):
            block = block.replace(loc, loc[: -len("index.html")])
            rewritten += 1
        return block

    updated = SITEMAP_URL_RE.sub(visit, text)
    if updated != text:
        write_replacing(sitemap, updated)
    report(f"finish-alias-stubs: sitemap {rewritten} rewritten, {dropped} dropped")


def main() -> int:
    if not OUTPUT_DIR.is_dir():
        raise SystemExit(f"finish-alias-stubs: no output directory at {OUTPUT_DIR}")

    base = site_url()
    patched = 0

    for path in sorted(OUTPUT_DIR.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        if not is_stub(text):
            continue
        if 'rel="canonical"' in text:
            continue  # already processed

        target = target_of(text)
        if target is None:
            report(f"finish-alias-stubs: no target found in {path}, skipping")
            continue

        # Resolve the destination relative to the stub's own directory, so the
        # canonical is site-absolute while the refresh stays relative.
        stub_dir = path.parent.relative_to(OUTPUT_DIR).as_posix()
        stub_dir = "" if stub_dir == "." else stub_dir
        destination = posixpath.normpath(posixpath.join(stub_dir, target))

        # The canonical names the directory form, matching what Quarto puts in
        # the destination page's own canonical and what tidy_sitemap advertises.
        # The refresh below keeps the literal `index.html` path, because that one
        # has to resolve as a relative file reference from the stub.
        canonical_path = destination
        if canonical_path.endswith("index.html"):
            canonical_path = canonical_path[: -len("index.html")]
        canonical = f"{base}/{canonical_path}"

        # Borrow the destination's own description and title. A stub that
        # describes where it points is more useful to a searcher than any
        # boilerplate about redirection, and it keeps the two in step for free.
        destination_file = OUTPUT_DIR / destination
        description = title = None
        if destination_file.is_file():
            destination_text = destination_file.read_text(encoding="utf-8")
            found = DESCRIPTION_RE.search(destination_text)
            description = found.group(1) if found else None
            found = TITLE_RE.search(destination_text)
            title = found.group(1).strip() if found else None
        else:
            report(f"finish-alias-stubs: {path} points at missing {destination_file}")

        if not description:
            description = f"This page has moved. Continue to {canonical}."

        head = [
            f'<meta http-equiv="refresh" content="0; url={html.escape(target, quote=True)}">',
            f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">',
            f'<meta name="description" content="{html.escape(description, quote=True)}">',
        ]
        text = text.replace("<head>", "<head>\n  " + "\n  ".join(head), 1)

        # The stub's <title> is the literal word "Redirect", which is also what
        # an audit reports as a non-descriptive title.
        if title:
            text = text.replace(
                "<title>Redirect</title>", f"<title>{html.escape(title)}</title>", 1
            )

        # The target is echoed a second time inside the script; fix it there too
        # so the browser path and the crawler path agree.
        match = REDIRECTS_RE.search(text)
        if match:
            repaired = json.dumps({"": target})
            text = text[: match.start(1)] + repaired + text[match.end(1) :]

        write_replacing(path, text)
        report(f"finish-alias-stubs: {path} -> {destination}")
        patched += 1

    report(f"finish-alias-stubs: {patched} stub(s) patched")
    tidy_sitemap(base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
