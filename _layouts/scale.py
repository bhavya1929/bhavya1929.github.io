#!/usr/bin/env python3
"""
resize-content.py — rescale the Experience / Publications page content.

Every font size, padding, gap, and card width in these two layouts is
written in fixed px (not rem — this site's Bootstrap sets 1rem = 10px,
which would silently break rem-based sizing here). This script scales
those px values by a percentage you choose, so you don't have to hunt
through the CSS by hand.

IMPORTANT: this scales whatever is CURRENTLY in the file, not some
stored "original" size. Running it twice compounds:
    90 then 90  ->  81% of where you started, not 90%.
If you want to go back, use git:
    git checkout -- _layouts/experience.html _layouts/publications.html

USAGE
    python3 scripts/resize-content.py 90                 # both files, 90% of current size
    python3 scripts/resize-content.py 110                # both files, 10% BIGGER
    python3 scripts/resize-content.py 95 experience       # just the experience page
    python3 scripts/resize-content.py 95 publications      # just the publications page
    python3 scripts/resize-content.py 90 --dry-run         # show what WOULD change, don't write

WHAT IT TOUCHES
    Only the <style> block's px values (font-size, padding, margin, gap,
    border-radius, grid-template-columns widths, etc.) inside
    _layouts/experience.html and/or _layouts/publications.html.

WHAT IT LEAVES ALONE
    - Values of 2px or smaller (hairline borders, thin shadow offsets) —
      scaling these makes borders render blurry, so they're skipped.
    - _includes/bd-theme.html is never touched by this script. That file
      controls the shared page title / avatar band, which is deliberately
      kept identical across Experience, Publications, AND Activities.
      If you ever want to resize that too, do it by hand or ask for a
      second script — don't point this one at it.
    - _layouts/activities.html is never touched either, on purpose.
"""

import re
import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> repo root

FILES = {
    "experience": REPO_ROOT / "_layouts" / "experience.html",
    "publications": REPO_ROOT / "_layouts" / "publications.html",
}


def scale_content(text: str, factor: float):
    changed = 0

    def repl(m):
        nonlocal changed
        val = float(m.group(1))
        if val <= 2:  # protect hairline borders / shadow offsets
            return m.group(0)
        new = round(val * factor, 1)
        if new == int(new):
            new = int(new)
        changed += 1
        return f"{new}px"

    new_text = re.sub(r"(\d+(?:\.\d+)?)px", repl, text)
    return new_text, changed


def main():
    ap = argparse.ArgumentParser(description="Rescale px sizes in the Experience/Publications layouts.")
    ap.add_argument("percent", type=float, help="Target percentage of CURRENT size, e.g. 90 = shrink 10%%, 110 = grow 10%%")
    ap.add_argument("pages", nargs="*", default=[],
                     help="Which page(s) to resize: 'experience', 'publications', or omit for both")
    ap.add_argument("--dry-run", action="store_true", help="Show what would change without writing files")
    args = ap.parse_args()

    targets = args.pages if args.pages else list(FILES.keys())
    bad = [p for p in targets if p not in FILES]
    if bad:
        print(f"Unknown page(s): {', '.join(bad)}. Choose from: experience, publications")
        sys.exit(1)
    factor = args.percent / 100.0

    for name in targets:
        path = FILES[name]
        if not path.exists():
            print(f"  ! {path} not found — skipping")
            continue
        text = path.read_text()
        new_text, n = scale_content(text, factor)
        verb = "would change" if args.dry_run else "changed"
        print(f"{name}: {n} px values {verb} (scaled to {args.percent:.0f}% of current)")
        if not args.dry_run:
            path.write_text(new_text)

    if args.dry_run:
        print("\nDry run only — no files were written. Drop --dry-run to apply.")
    else:
        print("\nDone. Run `bundle exec jekyll serve` and check the pages.")
        print("Not happy with it? git checkout -- <file> to revert, then try a different percentage.")


if __name__ == "__main__":
    main()
