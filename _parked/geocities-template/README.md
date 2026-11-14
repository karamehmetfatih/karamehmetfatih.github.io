# ~mfkara — GeoCities-style Quarto portfolio

A personal homepage built with [Quarto](https://quarto.org) and a hand-made
1990s GeoCities theme. No Bootstrap, no frameworks — just tables, marquees and love.

## House colour

Everything on the site is built from one chip:

| | Colour | Value |
|---|---|---|
| 🥬 | **Lettuce Green** | **PANTONE 13-0324 TCX** · `#BED38E` · `rgb(190, 211, 142)` |
| 🌿 | Leaf mid / deep | `#8FAE62` · `#5B7A3A` (borders, headings) |
| 🌱 | Stem / soil shade | `#38512A` · `#22331A` (sidebar, page background) |
| 🥗 | Panel tints | `#EDF5DC` · `#FAFCF2` |
| 🔴 | Radish red | `#C8395B` (the "hot" 1998 accent: hover, NEW!) |
| 🟡 | Butter yellow | `#F0C040` (construction tape, nav titles) |
| 🔵 | Ink blue / plum | `#1C4F7C` · `#6B4E9B` (links, visited links) |

They are declared once as custom properties at the top of `assets/geocities.css`.
Change `--lettuce` there and the whole site follows.

## Build

```bash
quarto preview      # live preview while editing
quarto render       # builds the site into _site/ (and cv.pdf)
```

The CV PDF is produced by **Typst**, which ships inside Quarto — no LaTeX needed.

## Files

| File | What it is |
|---|---|
| `_quarto.yml` | Site config: theme, metadata, Open Graph, bibliography |
| `index.qmd`, `research.qmd`, `publications.qmd`, `cv.qmd`, `links.qmd`, `guestbook.qmd` | Pages — edit in Markdown |
| `references.bib` | **Your publications.** Paste BibTeX here; the page formats itself |
| `_includes/header.html` | Sidebar, nav, neighborhood switcher, marquee, construction banner |
| `_includes/footer.html` | Hit counter, webring, copyright |
| `assets/geocities.css` | Four themes: **LettucePatch** (default, the Pantone above), **RainForest**, **Area51**, **SiliconValley** |
| `assets/geocities.js` | Theme switcher, per-browser hit counter, sparkle trail |
| `assets/the-plant-journal.csl` | Citation style (swap for any style from the [CSL repo](https://github.com/citation-style-language/styles)) |
| `assets/social-card.svg/.png` | 1200×630 link-preview image |
| `assets/sprout.svg` | Pixel-art lettuce sprout logo / favicon (same palette) |

## Adding a publication

Paste one BibTeX entry into `references.bib` and re-render. That's it — the
publications page and the citation formatting update themselves.

Export BibTeX from ORCID (Works → Export), Zotero (right-click → Export) or
Google Scholar (the " icon).

Two gotchas:

- Keep `%` comments **between** entries, never inside `{ }` — the Typst PDF
  renderer rejects them, and it treats `@article` inside a comment as a new entry.
- Protect capitals and species names with braces: `title = {{Botrytis cinerea} in lettuce}`.

## Before you publish

1. **Set your real URL.** `site-url` in `_quarto.yml` is `https://mfkara.net` —
   change it if the site lives elsewhere. Open Graph cards need an absolute URL.
2. **Fill in the TODOs.** Search the project for `TODO`: mostly dates and the
   exact thesis title in `cv.qmd` and `references.bib`.

## Tricks you can use in any page

```markdown
<span class="blink">blinking text</span>
<span class="rainbow">rainbow text</span>
<span class="new">NEW!</span>
::: gc-box
a ridged box
:::
::: gc-center
centred stuff
:::
<span class="gc-swatch"><i></i><b>Lettuce Green</b><span>#BED38E</span></span>
| a | table |
|---|---|
: {.gc-table}
```

Add `.gc-noprint` to anything that should vanish when printed.

To add a page: create `newpage.qmd` and add a link in `_includes/header.html`.
To change the default theme: edit `DEFAULT_THEME` in `assets/geocities.js`.
To re-colour the whole site: edit the palette block in `assets/geocities.css`
(and, if you want the link-preview card to match, re-export `assets/social-card.svg`
to `assets/social-card.png` at 1200×630).

## Accessibility

Visitors with "reduce motion" set in their OS get a static marquee, no blinking,
no sparkle trail — the look survives, the movement stops. The CV page has print
styles, so Ctrl-P gives a clean black-on-white document.

## Publish (free)

- **GitHub Pages:** `quarto publish gh-pages`
- **Netlify / Quarto Pub:** `quarto publish netlify` or `quarto publish quarto-pub`
- **Neocities** (the spiritual successor to GeoCities!): upload the contents of `_site/`.
