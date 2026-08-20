# Site TODO

Notes on the things only you can do. This file is not part of the site
(`_quarto.yml` renders `*.qmd` only), so it never reaches the published pages.

## 1. Delete about.qmd — required, the merge is incomplete without it

Home and About are now merged into `index.qmd`. The old page file is still there
because this environment blocked deletions from the shell:

```bash
git rm about.qmd
```

This matters more than it looks. `index.qmd` claims `/about.html` as an alias so the
old URL redirects to the homepage — but while `about.qmd` still exists it wins that
path, **silently**, with no render error. The result is a stale duplicate About page
still live at `/about.html`, unreachable from the navbar but indexed and linkable.
Verified: with `about.qmd` present the alias is discarded; once removed,
`/about.html` correctly becomes a redirect to `/`.

## 2. Affiliation — check the wording

Taken from your Gravatar card ("PhD @ UoY"), `index.qmd` says:

> I am a PhD researcher at the University of York.

Expand with the group/department if you like. Note the card gives your location as
Ankara, Türkiye while the affiliation is York — if that needs explaining to a
visitor, the merged homepage is now the place to do it.

## 3. Education and experience

These were dropped rather than left as empty headings. Paste into `index.qmd`
above "Selected publication" once you have the details:

```markdown
## Education

**PhD in ...** — University of ..., 20XX–20XX
**MSc in ...** — University of ..., 20XX–20XX
**BSc in ...** — University of ..., 20XX–20XX

## Experience

**Position** — Group / Department, Institution, 20XX–present
```

## 4. Placeholder blog post

`posts/deneme/index.qmd` is still the Quarto template's demo post ("Post With Code",
body text "Deneme 2" / "Deneme 3", dated 2021). It is the only entry on the Blog
listing:

```bash
git rm -r posts/deneme
```

If you remove it and have no other posts, consider dropping "Blog" from the navbar
too, so visitors do not land on an empty listing. That would leave a two-item
navbar (Home, Publications) — at which point the site is arguably one page plus a
publication list, which is a perfectly good academic site.

## 5. img/profile.jpg is now unused on-page

The merge dropped Quarto's `about: trestles` block, which was the only thing
displaying `img/profile.jpg`. Keep the file — it is still the Open Graph preview
image (`image: /img/profile.jpg` in `_quarto.yml`), so link previews depend on it.

## 6. Contact form — connected, but send one test message

The form posts to Formspree form `mgawdaja`. Integration is the AJAX pattern:
`fetch` POST with `Accept: application/json`, so the visitor stays on the page.

**Formspree requires you to confirm the address on the first submission.** Send
yourself one test message from the live site after deploying; Formspree emails
you a confirmation link, and submissions only start being delivered once you
click it. Until then the form will appear to work but mail will not arrive.

Free tier is 50 submissions/month. Formspree receives the name, email and
message that visitors type, so it is a data processor for your site.

## 7. Consider a CV page

Still the most common thing visitors to an academic homepage look for.
